import functions

chat_id = functions.get_chat_id()
text = "这是来自来福的祝福，祝您幸福安康！"
functions.tg_send_message(chat_id=chat_id, text=text)