import tkinter as tk
from tkinter import font
import json
import threading
import yarp


class ChatViewerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Viewer")  # Window title

        # Set lavender background color for the entire window
        lavender_bg = "#e6e6fa"
        self.root.configure(bg=lavender_bg)

        # Define main font for the chat text display
        self.big_font = font.Font(family="Arial", size=30)

        # Try to use a font that supports emoji; fallback if not available
        try:
            self.emoji_font = font.Font(family="Symbola", size=30)
        except:
            self.emoji_font = self.big_font  # fallback to main font

        # Create a frame inside the root to contain text widget and scrollbar
        frame = tk.Frame(root, bg=lavender_bg)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Create a Text widget for displaying messages, with word wrapping and custom styling
        self.text_widget = tk.Text(
            frame,
            wrap="word",
            font=self.big_font,
            bg=lavender_bg,
            fg="black",
            spacing3=5,  # space between paragraphs
            insertbackground="black"  # cursor color
        )
        self.text_widget.pack(side="left", fill="both", expand=True)

        # Create a vertical scrollbar and link it to the text widget
        scrollbar = tk.Scrollbar(frame, command=self.text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_widget.config(yscrollcommand=scrollbar.set)

        # Configure tags to style text differently depending on role
        self.text_widget.tag_config("user_human", foreground="black", font=self.big_font, spacing3=10)
        self.text_widget.tag_config("assistant", foreground="blue", font=self.big_font)
        self.text_widget.tag_config("tool", foreground="green", font=self.big_font)
        self.text_widget.tag_config("emoji", font=self.emoji_font)
        self.text_widget.tag_config("tool_indent", lmargin1=40, lmargin2=40)  # indent for tool text

        # Entry field for user input (multi-line text box)
        self.entry = tk.Text(root, height=3, font=self.big_font, bg=lavender_bg)
        self.entry.pack(padx=10, pady=(0, 10), fill="x")
        self.entry.bind("<Return>", self.on_enter_pressed)  # Bind Enter key to send message

        # Send button to manually send typed messages
        send_button = tk.Button(root, text="Send", command=self.send_message_bar, font=self.big_font, bg=lavender_bg)
        send_button.pack(pady=(0, 10))

        # Initialize YARP network (required before using any YARP functionality)
        yarp.Network.init()
        # Create a buffered port to receive messages from the agent
        self.yarp_port = yarp.BufferedPortBottle()
        # Open the port with the name /chat_viewer:i (input port)
        self.yarp_port.open("/chat_viewer:i")
        # Connect the agent's output port to this input port
        yarp.Network.connect("/agent/text:o", "/chat_viewer:i")

        # Start a background thread that continuously listens for incoming YARP messages
        self.running = True
        threading.Thread(target=self.listen_to_agent, daemon=True).start()

    def send_message_bar(self):
        # Get the user's input text from the entry field
        text = self.entry.get("1.0", "end-1c").strip()
        if text:
            # Display user's message in the chat window
            self.display_message("user_human", text)
            # Clear the entry field after sending
            self.entry.delete("1.0", "end")

    def on_enter_pressed(self, event):
        # If Shift is held, allow newline, otherwise send message
        if event.state & 0x0001:  # Shift key mask
            return
        self.send_message_bar()
        return "break"  # prevent default newline behavior on Enter

    def display_message(self, role, content, tool_call=False):
        # Insert message text into the text widget with styling based on the role
        if role == "tool" and tool_call:
            self.text_widget.insert("end", content + "\n\n", ("tool", "tool_indent", "emoji"))
        elif role == "assistant":
            self.text_widget.insert("end", content + "\n\n", ("assistant", "emoji"))
        elif role == "user_human":
            self.text_widget.insert("end", content + "\n\n", ("user_human", "emoji"))
        else:
            self.text_widget.insert("end", content + "\n\n", role)
        # Scroll to the end to show the latest message
        self.text_widget.see("end")

    def listen_to_agent(self):
        # Continuously listen for incoming messages on the YARP port
        while self.running:
            if self.yarp_port.getPendingReads() > 0:
                bottle = self.yarp_port.read(False)
                if bottle is not None and bottle.size() > 0:
                    try:
                        # Extract the JSON string from the first element of the bottle
                        msg_json = bottle.get(0).asString()
                        # Parse JSON string into a dictionary
                        msg_dict = json.loads(msg_json)
                        # Extract role and content from the message
                        role = msg_dict.get("role", "assistant")
                        content = msg_dict.get("content", "")
                        tool_call = role == "tool"
                        # Schedule display_message to run in the Tkinter main thread (thread-safe)
                        self.root.after(0, self.display_message, role, content, tool_call)
                    except Exception as e:
                        print("Error parsing YARP message:", e)

    def close(self):
        # Called when the window is closing: clean up resources
        self.running = False  # stop listening thread
        self.yarp_port.close()  # close YARP port
        yarp.Network.fini()  # finalize YARP network
        self.root.destroy()  # close the Tkinter window


if __name__ == "__main__":
    # Create main Tkinter window and run the ChatViewerGUI app
    root = tk.Tk()
    app = ChatViewerGUI(root)
    # Override window close button to call app.close()
    root.protocol("WM_DELETE_WINDOW", app.close)
    # Start Tkinter event loop
    root.mainloop()
