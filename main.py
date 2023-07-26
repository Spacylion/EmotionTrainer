import tkinter as tk
import random
import time
from tkinter import messagebox
from PIL import ImageTk, Image
import cv2

emotions = {
    "Радость": "assets/happy.mp4",
    "Страх": "assets/fear.mp4",
    "Злость": "assets/angry.mp4",
    "Презрение": "assets/contempt.mp4",
    "Отвращение": "assets/disgusted.mp4",
    "Грусть": "assets/sad.mp4"
}

score = 0
attempts = 0
remaining_questions = 10
current_emotion = None
video_canvas = None
score_label = None
question_label = None
emotion_buttons = []
start_button = None
next_button = None
countdown_label = None
difficulty_var = None
difficulty_radio = []

difficulty_map = {
    "Реальное время": 1.0,
    "Медленно": 0.5,
    "Очень медленно": 0.25
}


def select_difficulty():
    global difficulty_radio, start_button

    for btn in difficulty_radio:
        btn.config(state=tk.DISABLED)

    start_button.config(state=tk.NORMAL)


def start_quiz():
    global start_button, difficulty_radio, next_button, countdown_label, video_canvas, remaining_questions

    start_button.config(state=tk.DISABLED)
    countdown_label.config(text="")

    selected_difficulty = difficulty_var.get()
    countdown(3, selected_difficulty)


def countdown(seconds, difficulty):
    if seconds > 0:
        countdown_label.config(text=seconds)
        countdown_label.after(1000, countdown, seconds - 1, difficulty)
    elif seconds == 0:
        countdown_label.config(text="")
        start_emotion_quiz(difficulty)


def start_emotion_quiz(difficulty):
    global current_emotion, video_canvas, score_label, question_label, next_button, emotion_buttons

    # Select a random emotion
    current_emotion = random.choice(list(emotions.keys()))

    # Load and display the emotion video
    video_path = emotions[current_emotion]
    cap = cv2.VideoCapture(video_path)

    # Get video dimensions
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Calculate the appropriate height of the middle section to fit the video without deformation
    middle_section_height = int((height / width) * video_canvas.winfo_width())

    # Create a canvas to display the video frames
    video_canvas.config(width=width, height=middle_section_height)
    video_canvas.video_cap = cap  # Store the video capture object for future reference

    # Start displaying the video frames with the specified difficulty
    show_next_frame(difficulty)

    # Disable difficulty selection during the test
    next_button.config(state=tk.DISABLED)


def show_next_frame(difficulty=1.0):
    global video_canvas, next_button

    # Check if video capture is available
    if hasattr(video_canvas, "video_cap"):
        cap = video_canvas.video_cap

        # Read the next frame
        ret, frame = cap.read()

        if ret:
            # Convert the frame to PIL ImageTk format
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
            frame = frame.resize((video_canvas.winfo_width(
            ), video_canvas.winfo_height()), Image.LANCZOS)  # Resize frame
            frame = ImageTk.PhotoImage(frame)

            # Update the video canvas with the new frame
            video_canvas.image = frame
            video_canvas.create_image(0, 0, anchor=tk.NW, image=frame)

            # Calculate the time delay for the next frame update based on difficulty
            frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
            speed_factor = difficulty_map[difficulty]
            delay = int(1000 / (frame_rate * speed_factor))

            # Schedule the next frame update
            video_canvas.after(delay, show_next_frame, difficulty)
        else:
            # Video has ended, release the capture and enable emotion buttons for the current quiz
            cap.release()
            enable_emotion_buttons()
            next_button.config(state=tk.NORMAL)


def enable_emotion_buttons():
    for btn in emotion_buttons:
        btn.config(state=tk.NORMAL)


def disable_emotion_buttons():
    for btn in emotion_buttons:
        btn.config(state=tk.DISABLED)


def check_answer(selected_emotion):
    global current_emotion, score, attempts, remaining_questions, score_label, question_label

    attempts += 1

    if selected_emotion == current_emotion:
        # Correct answer
        score += 1
        score_label.config(text="Счет: {}/10".format(score), fg="green")

    if remaining_questions > 1:
        # Continue to the next question
        remaining_questions -= 1
        question_label.config(
            text="Вопрос {}/10".format(10 - remaining_questions))

        # Disable emotion buttons until the next video is shown
        disable_emotion_buttons()

        # Enable the next question button
        next_button.config(state=tk.NORMAL)

    else:
        # Quiz is complete
        show_results()


def show_results():
    global score, attempts

    # Calculate the score percentage
    score_percentage = (score / 10) * 100

    # Determine the mark based on the score percentage
    if score_percentage >= 90:
        mark = 5
    elif 75 <= score_percentage < 90:
        mark = 4
    elif 60 <= score_percentage < 75:
        mark = 3
    else:
        mark = 2

    # Show the results in a message box
    messagebox.showinfo("Тренировка завершена",
                        "Тренировка завершена!\nИтоговый счет: {}/10\nПопыток: {}\nСложность: {}\nОценка: {}".format(
                            score, attempts, difficulty_var.get(), mark))
    reset_quiz()  # Reset the quiz after showing the results


def reset_quiz():
    global score, attempts, remaining_questions, score_label, question_label, next_button, emotion_buttons

    score = 0
    attempts = 0
    remaining_questions = 10

    # Reset UI elements
    score_label.config(text="Счет: 0/10", fg="black")
    question_label.config(text="Вопрос 1/10")

    # Enable difficulty selection and disable other buttons
    for btn in emotion_buttons:
        btn.config(state=tk.DISABLED)
    start_button.config(state=tk.DISABLED)
    next_button.config(state=tk.DISABLED)

    for btn in difficulty_radio:
        btn.config(state=tk.NORMAL)


def next_question(difficulty):
    global current_emotion, remaining_questions, next_button, question_label, emotion_buttons

    next_button.config(state=tk.DISABLED)
    question_label.config(text="Вопрос {}/10".format(10 - remaining_questions))

    # Enable emotion buttons for the next question
    enable_emotion_buttons()

    # Proceed to the next question after the countdown
    countdown(3, difficulty)


def create_application():
    global video_canvas, score_label, question_label, next_button, start_button, countdown_label, difficulty_var, difficulty_radio, emotion_buttons

    root = tk.Tk()
    root.title("Тренажер распознавания эмоций")
    root.attributes("-fullscreen", True)
    root.configure(bg="#ffffff")

    # Set background image
    bg_image = Image.open("assets/bg.png")
    bg_image = bg_image.resize(
        (root.winfo_screenwidth(), root.winfo_screenheight()), Image.NEAREST)
    bg_photo = ImageTk.PhotoImage(bg_image)

    bg_label = tk.Label(root, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0)

    left_section = tk.Frame(root, bg="#ffffff", bd=10, relief="solid")
    left_section.place(relx=0.1, rely=0.1, relwidth=0.2, relheight=0.8)

    info_label = tk.Label(left_section, text="Тренажер распознавания эмоций", font=(
        "Helvetica", 16, "bold"), bg="#ffffff")
    info_label.pack(pady=10)

    info_text = "Данный тренажер предназначен для обучения распознаванию эмоций по видео.\n" \
                "Выберите сложность и нажмите кнопку 'Начать', чтобы начать тренировку. После этого " \
                "вам будет предложено определить эмоцию по видео, выбрав одну из предложенных эмоций " \
                "кнопками. После выбора эмоции, нажмите кнопку 'Следующий вопрос', чтобы продолжить.\n" \
                "\n" \
                "Тренажер подготовлен при поддержке НОЦ ИЭСБТТС при СПбГЭТУ «ЛЭТИ»." \
                "Является частью программу обучения кадровому профайлингу, в котором" \
                "подробно рассказывается принципы выявления микроэкспрессий лица." \
                "Является прототипом, образец для демонастрации уникального продукта." \
                "Ожидаются дополнения в разработке." \


    info_text_label = tk.Label(left_section, text=info_text, font=("Helvetica", 12), bg="#ffffff", wraplength=280,
                               justify="left")
    info_text_label.pack(pady=5)

    middle_section = tk.Frame(root, bg="#ffffff", bd=10, relief="solid")
    middle_section.place(relx=0.35, rely=0.15, relwidth=0.3, relheight=0.6)
    video_canvas = tk.Canvas(middle_section, bg="#000000")
    video_canvas.pack(fill=tk.BOTH, expand=True)

    right_section = tk.Frame(root, bg="#ffffff", bd=10, relief="solid")
    right_section.place(relx=0.7, rely=0.1, relwidth=0.2, relheight=0.8)

    difficulty_label = tk.Label(
        right_section, text="Выберите сложность:", font=("Helvetica", 14), bg="#ffffff")
    difficulty_label.pack(pady=20)

    difficulty_var = tk.StringVar(value="Реальное время")
    difficulty_options = ["Реальное время", "Медленно", "Очень медленно"]
    for i, option in enumerate(difficulty_options):
        btn = tk.Radiobutton(right_section, text=option, font=("Helvetica", 12), bg="#ffffff",
                             variable=difficulty_var, value=option, command=select_difficulty)
        btn.pack(pady=5)
        difficulty_radio.append(btn)

    score_label = tk.Label(right_section, text="Счет: 0/10",
                           font=("Helvetica", 16, "bold"), bg="#ffffff")
    score_label.pack(pady=20)

    question_label = tk.Label(
        right_section, text="Вопрос 1/10", font=("Helvetica", 14), bg="#ffffff")
    question_label.pack()

    emotions_frame = tk.Frame(right_section, bg="#ffffff")
    emotions_frame.pack(pady=20)

    for emotion in emotions:
        btn = tk.Button(emotions_frame, text=emotion, font=("Helvetica", 12), bg="#ffffff",
                        command=lambda emotion=emotion: check_answer(emotion))
        btn.pack(pady=5)
        emotion_buttons.append(btn)

    countdown_label = tk.Label(right_section, font=(
        "Helvetica", 48, "bold"), bg="#ffffff")
    countdown_label.pack(pady=20)

    start_button = tk.Button(right_section, text="Начать", font=("Helvetica", 16), bg="#ffffff", bd=5,
                             command=start_quiz, state=tk.DISABLED)
    start_button.pack(pady=20)

    next_button = tk.Button(right_section, text="Следующий вопрос", font=("Helvetica", 16), bg="#ffffff", bd=5,
                            command=lambda: next_question(difficulty_var.get()), state=tk.DISABLED)
    next_button.pack(pady=5)

    root.mainloop()


create_application()
