# No-subscription demo hosting: GitHub Codespaces

Research checked on 5 November 2026. This is the recommended temporary hackathon/demo option for the existing x86 Docker stack, not an always-on production hosting promise. No Codespace or paid resource has been created by preparing these files.

## Why this option

[GitHub Free personal accounts include 120 core-hours and 15 GB-month of Codespaces storage](https://docs.github.com/en/billing/reference/product-usage-included). A two-core Codespace consumes two core-hours per running hour, so a completely unused allowance covers up to 60 running hours/month. Other Codespaces, builds and stored environments consume the same allowance; check the actual remainder before creating this one. Storage usage continues while a Codespace is stopped. Delete the demo environment after backing up anything needed when the event is over.

Set or verify a **$0 Codespaces budget with “Stop usage when budget limit is reached” enabled**. Do not increase it, add paid capacity or buy compute for this deployment. If the included allowance is exhausted, stop rather than charging. Meta API consumption is separate from hosting; the demo limits it to 10 requests/hour globally and 2/hour per submitted owner handle, but this is not a dollar spending cap.

The app image was tested on Linux with 4 GB RAM / 2 CPU, real OCR/Presidio, visitor isolation and restart persistence. The prepared Codespaces host requests 2 CPU / 8 GB RAM so there is room for Docker and the editor. Only the web/API port is forwarded. Each public visitor still gets an isolated signed demo session; no developer reports are uploaded.

## Launch

1. Verify the allowance and $0 stop budget in the GitHub account's Codespaces billing settings. A GitHub connector for repository access does not prove access to this billing setting.
2. Open [a new Codespace for this repository](https://codespaces.new/Nurzhan-Zhumabekov/META). Use the two-core machine and the supplied `.devcontainer/devcontainer.json`. Do not enable paid prebuilds.
3. Add `META_API_KEY` as a **Codespaces secret**, scoped only to `Nurzhan-Zhumabekov/META`. This is distinct from an Actions secret. Never commit it. Restart the Codespace after adding it.
4. Run `bash .devcontainer/start.sh`. The script generates an ignored, private session-signing secret, builds the image, starts the isolated public-demo mode and waits for health. It does not automatically expose a public port.
5. In the Ports panel, make **only port 8090 Public**. [GitHub supports sharing forwarded ports publicly](https://docs.github.com/en/codespaces/developing-in-a-codespace/forwarding-ports-in-your-codespace). Copy its actual `https://…-8090.app.github.dev` URL; do not invent a deployment URL.
6. At that URL, verify health, real Meta mode, one live report, explained confirmation, scoped appeal/overturn and two-visitor isolation. Only then call the demo publicly deployed. Stop the Codespace when finished.

The address works while the Codespace is running. Idle shutdown and exhausted quotas can make it unavailable. Forwarded public ports may revert to private after a restart. Data lives in that Codespace's Docker volume and is not a durable backup; deleting the Codespace loses it. This fits an attended demonstration, not unattended judge access at any time.

## Other researched options

| Option | Current limitation for MirrorCheck |
| --- | --- |
| [Hugging Face Docker Spaces](https://huggingface.co/docs/hub/spaces-overview) | Creation now requires PRO/Team/Enterprise even though CPU Basic has no hourly price. Not a zero-subscription recommendation. |
| [Oracle Always Free](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm) | Current Always Free A1 allowance is 2 OCPUs / 12 GB RAM, subject to regional capacity and idle reclamation. ARM deployment is not verified: pinned PaddlePaddle 3.3.1 publishes Linux x86-64 wheels, so the tested Docker image is not ARM-native. The AMD free micro VM has 1 GB, below the tested configuration. |
| [Google Cloud Run](https://cloud.google.com/run/pricing) | Useful free request/CPU/RAM quotas, but requires billing and can charge above quotas or for other resources. Not a strict zero-cost guarantee. |
| [Northflank Sandbox](https://northflank.com/pricing) | Free resources are limited; current billing documentation and the pricing page differ about card requirements. The complete 4 GB stack has not been verified in its free resource allocation. |
| Static frontend hosting | Can serve the landing/video/results, but cannot run PaddleOCR, Presidio and the Python API by itself. It would not be the complete live detector. |

For continuous independent hosting, Oracle Always Free is worth a separate ARM-compatibility investigation after account access and regional capacity are confirmed. Codespaces is the fastest prepared demo path using the current tested image.
