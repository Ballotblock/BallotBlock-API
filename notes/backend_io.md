# About BackendIO
Despite the project's name, ``BallotBlock`` does not require that the user deploying the system utilizes a blockchain based backend to actually store data. Due to the centralized nature of the project, Blockchain technology does not automatically make the project more secure. A ``HyperLedger`` based backend is included in the application due to a non-neogtiable request from our project sponsor, Statefarm.  End users are free to store their data on a Blockchain / Non-Blockchain based database.

The ``intermediary.py`` file in this project repo is the main HTTP API that clients interact with.

Clients send HTTP ``GET`` and ``POST`` requests to the server (along with accompanying JSON) and it will perform the necessary actions based off that data.

When it comes to actually storing that data, BallotBlock utilizes a backend agnostic approach by providing a ``BackendIO`` interface in ``src/interfaces/backend_io.py``

If a user wanted to deploy ``BallotBlock`` to hold elections in their organization, but they wanted to store all voting data using ``MongoDB``, then they could create a ``MongoDBBackendIO`` that implemented the ``BackendIO`` interface.

In ``intermediary.py`` they just have to set the ``BACKEND_IO`` variable equal to a new instance of their class and the rest of the system will automatically work and correctly store data on their preferred backend (provided the interface is implemented correctly).

# BallotBlock-API vs Your BackendIO's responsibilities
When you implement the ``BackendIO`` interface you're reponsible for **storing and retrieving data only**.

The ``BallotBlock`` server itself will handle:
* Encrypting data prior to storing it on the ``BackendIO``.
* Decrypting data prior to sending it to users.
* Removing election private keys from data retrieved from the ``BackendIO`` prior to sending it to users if the election is still in progress.
* Sanitizing and validating user data.
* Preventing unauthorized users from tampering with the database / blockchain.

Your ``BackendIO`` implementation doesn't need to (although it doesn't hurt to) check if
an election exists prior to creating a ballot for it etc. The ``BallotBlock`` server will
call the appropriate functions on your ``BackendIO`` to avoid invalidating the state of the actively used ``BackendIO``.

# Recommended Layout
In the provided reference ``SQLite3`` implementation, we utilize a total of three tables
to implement all the required methods:

| Table                  | Description  |
| -----------------------|--------------|
| Election               |Stores a list of all the created elections in the application. |
| ElectionParticipation  |Stores a list of usernames and elections that they have participated in. This table **SHOULD NOT** link a user directly to a record in the Ballot table. It should only mark if they have participated in a given election or not.       |
| Ballot                 |A list of ballots and their encrypted answers. Random uuid's are used to link a voter to a ballot.|

The relationships between the tables are defined as follows:
* The ``Election`` table has no constraints or foreign keys.
* In the ``ElectionParticipation`` table, each record should have a 1:1 correspondance with a specific Election (but not a specific Ballot!)
* In the ``Ballot`` table, each record should have a 1:1 correspondance with a specific Election.

The reference ``SQLite3`` implementation uses ``FOREIGN KEY``'s and ``UNIQUE`` constraints as a sanity check but the ``BallotBlock`` API will maintain this referential integrity for you by calling the appropriate methods prior to storing anything on the actively used ``BackendIO``.

# General details
* All keys passed into the ``BackendIO`` methods are strings.
* All values passed into the ``BackendIO`` methods are strings with the exception of the ``"start_date"`` and ``"end_date"`` keys. (The values are integers.)

# Method details.
Please see ``src/interfaces/backend_io.py`` for specific details about each method that needs to be implemented for a correct implementation of the ``BackendIO`` interface.

You can also study the ``src/sqlite/sqlite_backend_io.py`` and ``src/sqlite/sqlite_queries.py`` files to model your own ``BackendIO`` implementation after it.
