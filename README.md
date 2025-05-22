# Telegram Reservation Bot for [UCSC Bistro](https://dining.ucsc.edu/university-center-bistro-cafe/index.html)

This is a Telegram bot I built to automate table reservations at the UCSC Bistro — a popular campus restaurant that's always fully booked during lunch hours.

## 🛠 Project Background

After multiple failed attempts to reserve a table manually through the restaurant's website, I decided to automate the process. Here's how it started:

- I inspected the reservation process using **Chrome Developer Tools**
- Found the API endpoint used for `POST /api/booking/insert`
- Replicated the request in **Postman** to test different parameters and headers
- Once confirmed, I built a fully functional **Telegram bot** to make real-time reservations directly via chat

## 🤖 What the Bot Can Do

The bot guides users through a step-by-step reservation process:

1. **Starts with any message or `/start`**
2. **Collects user input:**
   - Name
   - Email (validated)
   - US Phone number (10-digit only, validated)
   - Date (only weekdays, starting from tomorrow, limited to current or next month)
   - Time (between 11:30 and 14:00 in 15-minute intervals)
   - Party size (1 to 10 people)
3. **Displays a summary of entered data**
4. **Waits for user confirmation (`yes`)**
5. **Sends the reservation to the official restaurant API**
6. **Notifies user of success or failure**
7. **Users can stop the reservation process anytime with `/cancel`**

## 💡 Features

- Built using `aiogram 3.x` (async Python framework for Telegram bots)
- FSM (Finite State Machine) for managing conversation flow
- Input validation and user-friendly error messages
- Works entirely in Telegram — no web browser needed
- Graceful handling of API errors and malformed inputs

## 📦 Technologies Used

- Python 3.11
- aiogram 3.x
- `requests` for API interaction
- Telegram Bot API
- Chrome DevTools + Postman for reverse engineering

## 🧪 Example Conversation
![image](https://github.com/user-attachments/assets/abc5f74c-7abf-4d00-880a-6c33356205c2)

## 📌 Why This Matters

This project demonstrates:
- Practical use of reverse engineering and API interaction
- Integration of async Python frameworks with real-world systems
- A polished user experience delivered entirely through chat

## 🚀 Setup Instructions

1. Clone the repo
2. Create a `.env` file with your Telegram Bot Token
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Run the bot
```bash
python main.py
```
