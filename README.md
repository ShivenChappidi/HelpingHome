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

Set the following environment variable:
- `OPENNOTE_API_KEY` - Your Opennote API key (get from https://www.opennote.com/)

