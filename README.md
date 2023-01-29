# Chat TCP Protocol

## Description
A TCP protocol I made to build a chat program.

## Notes
* The format of sending any request is the method a space and then all payloads seperated with spaces.
* Whenever sending payload, it is always going to be sent encoded with Base64 to allow all characters in payload, except for error messages.
* The methods and modes are uppercase to show they are commands while talking about it in chat.
* Permission level can range between 0 and 3

## Methods, Modes, and Errors that are passed using the protocol

### Methods
| Method and Payload           | Description                                                                      | For clients, servers, or both | Permissions required |
|------------------------------|:--------------------------------------------------------------------------------:|:------------------------------|:---------------------|
| READY                        | Tells the other side they are ready to accept commands, always used on connect   | Both                          | 0                    |
| CLOSE                        | Close connection.                                                                | Both                          | 0                    |
| LOGIN (username) (password)  | Making a login request with username and password to the server.                 | Client                        | 0                    |
| CONSOLE_LOG (message)        | Tells the server to log a message to the server logs.                            | Client                        | 2                    |
| ERROR (error message)        | Sends to the other side an error message, usually in response to another request | Both                          | 0                    |
| ACK                          | Acknowledging a request, usually means a request succeeded                       | Both                          | 0                    |

### Modes
| Mode        | Description                            |
|-------------|:---------------------------------------|
| TO          | Sending to the server                  |
| TO_TELNET   | Sending to the server in telnet mode   |
| FROM        | Sending from the server                |
| FROM_TELNET | Sending from the server in telnet mode |

### Error Messages
| Error          | Description                                         | Sent to clients, servers, or both |
|----------------|:---------------------------------------------------:|:----------------------------------|
| LoginRequired  | You need to login to run this command               | Clients                           |
| LoginFailed    | You sent an incorrect username or password          | Clients                           |
| InvalidB64Code | You sent invalid base64 code or undecodable strings | Both                              |
| InvalidCommand | You sent an invalid or non-existant command         | Both                              |
