# Chat TCP Protocol

## Description
A TCP protocol I made to build a chat program.

## Notes
* The format of sending any request is the method a space and then all payloads seperated with spaces.
* Whenever sending payload, it is always going to be sent encoded with Base64 to allow all characters in payload, except for error messages.
* The methods and modes are uppercase to show they are commands while talking about it in chat.
* Permission level can range between 1 and 4
* The mode FROM_TELNET does not send any response back to the server as if it is in telnet mode, it is meant to be read by humans.

## Methods, Modes, and Errors that are passed using the protocol

### Methods
| Method and Payload              | Description                                                                       | For clients, servers, or both | Permissions required |
|---------------------------------|:---------------------------------------------------------------------------------:|:------------------------------|:---------------------|
| SEND_TO_ID                      | Tells the client to send the ID given from the session in the TO mode.            | Client                        | 1                    |
| READY                           | Tells the other side they are ready to accept commands, always used on connect.   | Server                        | 1                    |
| CLOSE                           | Close connection.                                                                 | Both                          | 1                    |
| LOGIN (username) (password)     | Making a login request with username and password to the server.                  | Client                        | 1                    |
| GET_ID                          | Get the session ID.                                                               | Client                        | 1                    |
| ECHO_FROM (anything or nothing) | Sends the same message back through a FROM session.                               | Both                          | 1                    |
| CONSOLE_LOG (message)           | Tells the server to log a message to the server logs.                             | Client                        | 3                    |
| ERROR (error message)           | Sends to the other side an error message, usually in response to another request. | Both                          | 1                    |
| ACK                             | Acknowledging a request, usually means a request succeeded.                       | Both                          | 1                    |

### Modes
| Mode        | Description                            |
|-------------|:---------------------------------------|
| TO          | Sending to the server                  |
| TO_TELNET   | Sending to the server in telnet mode   |
| FROM        | Sending from the server                |
| FROM_TELNET | Sending from the server in telnet mode |

### Error Messages
| Error            | Description                                                                 | Sent to clients, servers, or both |
|------------------|:---------------------------------------------------------------------------:|:----------------------------------|
| LoginRequired    | You need to login to run this command                                       | Clients                           |
| LoginFailed      | You sent an incorrect username or password                                  | Clients                           |
| InvalidB64Code   | You sent invalid base64 code or undecodable strings                         | Both                              |
| InvalidCommand   | You sent an invalid or non-existant command                                 | Both                              |
| PermissionDenied | Your permission level is below the required level to issue the command      | Clients                           |
| NoFROMSession    | You sent a command that required a FROM session attached when there is none | Clients                           |
