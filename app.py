import gradio as gr

from src.pipeline import lookup, submit_claim


def on_submit(owner, suspect, original, suspect_img):
    if not (owner and suspect and original is not None and suspect_img is not None):
        return "Fill in all fields."
    c = submit_claim(owner, suspect, original, suspect_img)
    return f"Claim {c.id}: similarity {c.score:.0%}, status: {c.status}\n" + "\n".join(f"- {r}" for r in c.reasons)


def on_lookup(handle):
    rows = lookup(handle)
    if not rows:
        return "No claims for this account."
    return "\n".join(f"{r['id']}: {r['status']} (similarity {r['score']:.0%})" for r in rows)


with gr.Blocks(title="Fake Account Report") as demo:
    with gr.Tab("Report a fake"):
        owner = gr.Textbox(label="Your (original) handle")
        suspect = gr.Textbox(label="Suspected fake handle")
        orig_img = gr.Image(type="pil", label="Your profile screenshot")
        sus_img = gr.Image(type="pil", label="Suspected fake screenshot")
        out = gr.Textbox(label="Result")
        gr.Button("Submit claim").click(on_submit, [owner, suspect, orig_img, sus_img], out)
    with gr.Tab("Check an account"):
        h = gr.Textbox(label="Handle to check")
        res = gr.Textbox(label="Status")
        gr.Button("Check").click(on_lookup, h, res)

if __name__ == "__main__":
    demo.launch()
