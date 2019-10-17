# PYCHAT

## DESCRIPTION:
- A python implementation of a chat app using TCP sockets with Async I/O

## GETTING STARTED:
- In order to use this program, make sure you have python 3.6 and above already installed on the system.

### INSTALLING DEPENDENCIES:
Open a terminal and run the following command:

```bash
python3 -m pip install aioconsole
```
## USAGE:
Launch terminal and navigate to the PYCHAT directory.

Run the following command:

```bash
python3 chat.py
```

## FUNCTIONS:

- **help:** Display information about the available user interface options or command manual.

    Command Line Usage: 
    ```bash 
    help <function_name>
    ```
    #### Example:
    ```bash
    > help myip
    ```
    
- **myip:** Display the IP address of this process.
    Note: The IP should not be your “Local” address (127.0.0.1). It should be the actual IP of the computer.
    
    Command Line Usage: 
    ```bash
    myip
    ```
    #### Example:
    ```bash
    > myip
    192.168.1.8
    ```
    
- **myport:** Display the port on which this process is listening for incoming connections.

    Command Line Usage: 
    ```bash
    myport
    ```
    #### Example:
    ```bash
    > myport
    5000
    ```

- **connect:** This command establishes a new TCP connection to the specified ```<destination>``` at the specified ```<port no>```. The ```<destination>``` is the IP address of the computer.
 
    Command Line Usage: 
    ```bash
    connect <destination> <port no.>
    ```
    #### Example:
    ```bash
    > connect 192.168.1.8 5000
    ```

- **list:** Display a numbered list of all the connections this process is part of.
   
   Command Line Usage:
    ```bash
    list
    ```
    #### Example:
    ```bash
    > list
    ```

- **terminate:** This command will terminate the connection listed under the specified
    number when LIST is used to display all connections.

    Command Line Usage:
    ```bash
    terminate <id>
    ```
    
    #### Example:
    ```bash
    > terminate 2
    ```

- **send:** This command will send message to the host specified by ```<id>```

    Command Line Usage:
    ```bash
    send <id>
    ```
    #### Example:
    ```bash
    > send 3 Oh! This project is a piece of cake
    ```

- **exit:** Closes all the connections and terminate this process.

    Command Line Usage:
    ```bash
    exit
    ```

## CONTRIBUTORS:

- Austin Vargason:
    - Created Async sockets
    - Created functions/commands: connect, send, terminate, list, myport and terminate
    - Manage dependencies
- Mayank Saboo:
    - Made server socket to reuse it's address so hosts can connect same server
    - Created function/commands: exit, list, myip
    - Created README
