# HelpingHome

An application to assist people with autism in living independently using Indistinguishable From Magic hardware devices.

## Project Structure

- `rooms/` - Room-specific modules (kitchen, laundry, bathroom)
- `opennote/` - Opennote API integration for note-taking and journals
- `utils/` - Shared utilities and common functions
- `config/` - Configuration files

## Setup

### Dependencies

Install dependencies:
```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root with your API keys:
- `ELEVENLABS_API_KEY` - Your ElevenLabs API key for text-to-speech
- `OPENNOTE_API_KEY` - Your Opennote API key (get from https://www.opennote.com/)
- `IFMAGIC_API_KEY` - Your Indistinguishable From Magic API key (if needed)

Example `.env` file:
```
ELEVENLABS_API_KEY=your_key_here
OPENNOTE_API_KEY=your_key_here
IFMAGIC_API_KEY=your_key_here
```

**Note:** The `.env` file is already in `.gitignore` and will not be committed to git.

