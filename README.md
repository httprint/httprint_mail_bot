# HTTPrint Mail Bot

Mail Bot for uploading files to HTTPrint server

Runs on docker

## How to

### Docker

Add following settings to your`docker-compose.yml` file:

```yaml
  httprint_mail_bot:
    build: https://github.com/httprint/httprint_mail_bot.git
    container_name: httprint_mail_bot  # optional
    environment:
      - HTTPRINT_HOST=http://httprint.example.com:7777 # optional, defaults to http://httprint:7777
      - IMAP_HOST=imap.example.com
      - IMAP_USERNAME=noreply@example.com
      - IMAP_PASSWORD=password
      - IMAP_FOLDER=INBOX
      - SMTP_HOST=smtp.example.com
      - SMTP_USERNAME=noreply@example.com
      - SMTP_PASSWORD=password
      - SMTP_FROM=httprint <httprint@example.com>
      - LOG_LEVEL=DEBUG  # optional, defaults to INFO
    restart: unless-stopped
  ```
  


# License and copyright

Copyright 2023 itec <itec@ventuordici.org>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Printer icon created by Good Ware - Flaticon
