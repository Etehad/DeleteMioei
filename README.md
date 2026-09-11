# Delete Mio Messages

A Telethon user-account service that watches Telegram group `-1001715381518` and schedules message deletion.

## Rules

Messages are deleted after **1 minute** when:

- The entire trimmed message is exactly `مع`
- The entire trimmed message is exactly `میو`
- The entire trimmed message is exactly `ماهی`
- The entire trimmed message is exactly `یخچال میویی`
- The entire trimmed message is exactly `میو بانک`
- The entire trimmed message is exactly `بانک میویی`
- The entire trimmed message is exactly `کارخونه میویی`
- The message contains `میو پوینت`
- The message contains `رفت تو یخچال`

If none of the above rules matches, a message sent by Telegram user/bot ID `8299996037` is deleted after **10 minutes**.

All other messages are ignored.

## Environment variables

Set these on Render:

- `API_ID`
- `API_HASH`
- `TELEGRAM_SESSION`

Do **not** put the Telegram String Session in GitHub.

## Important Telegram permissions

The logged-in Telegram account must be a member of the target group and have enough administrator permissions to delete other users' and bots' messages.

## Deploying on Render

This project is configured as a Render Worker in `render.yaml`.

1. Create a GitHub repository.
2. Upload all project files.
3. Create a new Render service from the repository, or use the `render.yaml`.
4. Add the three environment variables.
5. Deploy.

The service must remain running continuously. A background worker is appropriate because the Telegram client needs a persistent connection.

## Security

The String Session is equivalent to a logged-in Telegram session. Never commit it to GitHub, paste it into source code, or share it publicly.

If a String Session is ever exposed, revoke that Telegram session from Telegram's active sessions and generate a new one.
