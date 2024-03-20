import shutil
from pathlib import Path

from sigexport import files, models, utils
from sigexport.logging import log


def merge_chat(new: list[models.Message], path_old: Path) -> list[models.Message]:
    """Merge new and old chat markdowns."""
    with path_old.open(encoding="utf-8") as f:
        old_raw = f.readlines()

    old = utils.lines_to_msgs(old_raw)
    old_msgs = [o.to_message() for o in old]

    try:
        a = old_raw[0][:30]
        b = old_raw[-1][:30]
        c = new[0].to_md()[:30]
        d = new[-1].to_md()[:30]
        log(f"\t\tFirst line old:\t{a}")
        log(f"\t\tLast line old:\t{b}")
        log(f"\t\tFirst line new:\t{c}")
        log(f"\t\tLast line new:\t{d}")
    except IndexError:
        log("\t\tNo new messages for this conversation")

    # get rid of duplicates
    msg_dict = {m.comp(): m for m in old_msgs + new}
    merged = list(msg_dict.values())

    return merged


def merge_with_old(
    chat_dict: models.Chats, contacts: models.Contacts, dest: Path, old: Path
) -> models.Chats:
    """Main function for merging new and old."""
    new_chat_dict: models.Chats = {}
    for key, msgs in chat_dict.items():
        name = contacts[key].name
        dir_old = old / name
        if dir_old.is_dir():
            log(f"\tMerging {name}")
            dir_new = dest / name
            if dir_new.is_dir():
                files.merge_attachments(dir_new / "media", dir_old / "media")
                try:
                    path_old = dir_old / "chat.md"
                    msgs_new = merge_chat(msgs, path_old)
                    new_chat_dict[name] = msgs_new
                except FileNotFoundError:
                    try:
                        path_old = dir_old / "index.md"  # old name
                        msgs_new = merge_chat(msgs, path_old)
                        new_chat_dict[name] = msgs_new
                    except FileNotFoundError:
                        log(f"\tNo old for {name}")
            else:
                shutil.copytree(dir_old, dir_new)
    return new_chat_dict
