import logging
from telethon import TelegramClient, events
import sqlite3
import os

class TelegramScraper:
    def __init__(self, api_id, api_hash, phone_number, channels, db_name='telegram_data.db'):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.channels = channels
        self.db_name = db_name
        self.client = TelegramClient('session_name', self.api_id, self.api_hash)

        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='telegram_scraping.log'
        )

    def init_db(self):
        """Initialize the SQLite database."""
        if not os.path.exists(self.db_name):
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel TEXT,
                    message TEXT,
                    media_url TEXT,
                    date TEXT
                )
            ''')
            conn.commit()
            conn.close()
            logging.info("Database initialized.")

    def save_to_db(self, channel, message, media_url, date):
        """Save scraped data to the database."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (channel, message, media_url, date)
            VALUES (?, ?, ?, ?)
        ''', (channel, message, media_url, date))
        conn.commit()
        conn.close()
        logging.info(f"Data saved to database: {channel} - {message[:50]}...")

    async def start_scraping(self):
        """Start the Telegram scraping process."""
        self.init_db()

        if not os.path.exists('media'):
            os.makedirs('media')  # Create a folder to store media files

        @self.client.on(events.NewMessage(chats=self.channels))
        async def handler(event):
            try:
                channel = event.chat.username or event.chat.title
                message = event.message.message
                media_url = None
                if event.message.media:
                    media_url = await event.download_media(file='media/')  # Save media to 'media/' folder
                date = event.message.date.isoformat()

                self.save_to_db(channel, message, media_url, date)
                logging.info(f"New message scraped from {channel}: {message[:50]}...")
            except Exception as e:
                logging.error(f"Error processing message: {e}")

        await self.client.start(self.phone_number)
        logging.info("Scraping started...")
        await self.client.run_until_disconnected()