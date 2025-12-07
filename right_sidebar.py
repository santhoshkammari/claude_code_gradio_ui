from a import gr
import time
import random


def user(user_message, history: list):
    return "", history + [{"role": "user", "content": user_message}]

def bot(history: list):
    bot_message = random.choice(["How are you?", "I love you", "I'm very hungry"])
    history.append({"role": "assistant", "content": ""})
    for character in bot_message:
        history[-1]['content'] += character
        time.sleep(0.05)
        yield history



def create_right_sidebar():
    with gr.Accordion("Chatbot", open=True):
        chatbot = gr.Chatbot()
        msg = gr.Textbox()
        msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
         bot, chatbot, chatbot
        )
    # with gr.Blocks():
    #     chatbot = gr.Chatbot()
    #     msg = gr.Textbox()
    #     msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
    #      bot, chatbot, chatbot
    #     )
    

