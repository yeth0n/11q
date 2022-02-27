import io
import sys
import traceback

from . import jmthon, edit_or_reply

plugin_category = "utils"


@jmthon.ar_cmd(
    pattern="حساب ([\s\S]*)",
    command=("حساب", plugin_category),
    info={
        "header": "لحل معادلة رياضيات بسيطه.",
        "description": "ااكتب الامر مع معادلة رياضيات بسيطه لحلها ",
        "usage": "{tr}حساب 2+9",
    },
)
async def calculator(event):
    "لحل معادلة رياضيات بسيطه."
    cmd = event.text.split(" ", maxsplit=1)[1]
    event = await edit_or_reply(event, "يتـم الـحساب أنتـظر قـليلا")
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    san = f"print({cmd})"
    try:
        await aexec(san, event)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "عـذرا لأ اسـتطيع ايجـاد حـل لهـكذا معـادلات"
    final_output = "السـؤال: {} \n\n الـحل: \n{} \n".format(
        cmd, evaluation
    )
    await event.edit(final_output)


async def aexec(code, event):
    exec("async def __aexec(event): " + "".join(f"\n {l}" for l in code.split("\n")))

    return await locals()["__aexec"](event)
