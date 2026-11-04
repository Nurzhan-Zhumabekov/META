FROM node:24-alpine AS frontend
WORKDIR /build/web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm test -- --maxWorkers=1 && npm run build

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    HOME=/home/mirrorcheck
ENV ML_MODEL_PATH=/app/models/profile_risk_model.json PAIR_ML_MODEL_PATH=/app/models/pair_risk_model.json
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 libglib2.0-0 libgl1 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -g 1000 mirrorcheck && useradd -u 1000 -g 1000 -m mirrorcheck
WORKDIR /app
COPY requirements-api.txt requirements-vision.txt requirements-privacy.txt ./
RUN python -m venv /opt/api && /opt/api/bin/pip install --no-cache-dir -r requirements-api.txt \
    && python -m venv /opt/privacy && /opt/privacy/bin/pip install --no-cache-dir -r requirements-privacy.txt \
    && /opt/privacy/bin/pip install --no-cache-dir https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
RUN python -m venv /opt/vision \
    && /opt/vision/bin/pip install --no-cache-dir torch==2.15.0+cpu torchvision==0.29.2+cpu --index-url https://download.pytorch.org/whl/cpu \
    && /opt/vision/bin/pip install --no-cache-dir -r requirements-vision.txt \
    && /opt/api/bin/pip check && /opt/privacy/bin/pip check && /opt/vision/bin/pip check
COPY src/ src/
COPY evidence_tools/ evidence_tools/
COPY models/ models/
COPY deploy/ deploy/
COPY --from=frontend /build/web/dist web/dist
RUN mkdir -p /app/outputs /home/mirrorcheck/.paddlex /home/mirrorcheck/.cache /var/data \
    && chown -R mirrorcheck:mirrorcheck /app /home/mirrorcheck /var/data
USER mirrorcheck
RUN /opt/privacy/bin/python -c "from evidence_tools.privacy import engine; engine()" \
    && /opt/vision/bin/python -c "from evidence_tools.vision import ocr_engine; ocr_engine()"
USER root
EXPOSE 8090
ENTRYPOINT ["python", "deploy/start.py"]

FROM runtime AS test
COPY tests/ tests/
COPY evals/ evals/
COPY vision_tests/ vision_tests/
COPY privacy_tests/ privacy_tests/
COPY scripts/install_demo_models.py scripts/install_demo_models.py
RUN /opt/api/bin/pip install --no-cache-dir pytest \
    && /opt/api/bin/python -m pytest tests -q --basetemp /tmp/api-tests \
    && /opt/privacy/bin/python -m pytest privacy_tests -q --basetemp /tmp/privacy-tests \
    && /opt/vision/bin/python -m pytest vision_tests -q --basetemp /tmp/vision-tests

FROM runtime AS release
