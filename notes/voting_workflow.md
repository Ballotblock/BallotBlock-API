# Logging In
The API endpoints ``/api/election/create`` and ``/api/election/vote`` are restricted to clients who are logged into the system and have a cookie that contains a valid SessionID
that the server has authenticated them with.

The user should send a JSON POST request with the following format.
```
{
    "username": "Your username",
    "password": "*********"
}
```

To the api endpoint ``/api/login``

The server will then ask the ``registration_server`` to validate that you have previously registered to vote.

For the purpose of this capstone, we have abstracted this responsibility away. In a real world usage scenario of our system, the deployers would implement the ``registration_server`` component. It would tie users in the system to some kind of real world unique human ID that they can control like a driver's license or passport. Abstracting this component away in our system allows us to mostly ignore the Sybil attack or the prescence of fraudlent voters in our system.

This cookie should be sent in subsequent requests to the server for actions that require authentication.

# Creating an Election:
After logging into the BallotBlock-API, if the user is an **ElectionCreator** and
they want to create an election in the system, then they must send a JSON POST
request with the following format:

```
{

    "master_ballot":
    "{
        "description": "Pick your favorite color / shape.",
        "election_title": "Favorite Color and Shape Election",
        "start_date": '2018-03-30T18:48:21.940478-07:00',
        "end_date": '2018-03-31T18:50:29.522627-07:00',
        "questions":
         [
            ["Favorite Color?", ["Red", "Blue"]],
            ["Favorite Shape?", ["Square", "Triangle"]]
         ]
    },
    "creator_public_key": "JKWPQH5Hi5v3iyFqyCKpdGncpvHnmsKK2ryz4uQkd4MBdOHbKrW4zgmIgH+myIatf/vb+l5eb0f79BGbMBc1jg==",
    "master_ballot_signature": 'XfNLc06Pp5O2xG9R4zH/qp2tPABG2wxCcO/BymLsRMATALnhdmrtX32sI+KaGgLhAriWgg2dm5wpeuk2bkmg8w=='
}
```

* ``master_ballot`` should be a JSON object in string (UTF-8) format.
    * ``description`` should be a UTF-8 string explaining the purpose of the election.
    * ``start_date`` should be a  ISO 8601 string indicating the start date of the election.
    * ``end_date`` should be a ISO 8601 string seconds indicating the end date of the election.
    * ``questions`` should be a array of arrays. The first value should be the question, the second value should be an array of expected answers. (TODO: Consider changing this so that the key is the question and the value is an array of allowed answers)
* ``creator_public_key`` key should be a **ecdsa.SECP256k1** public key in **base64** format.
* ``master_ballot_signature`` should be the ``master_ballot`` string but signed using the ``creator_public_key``'s corresponding private key.

This JSON POST should be sent to the server endpoint ```/api/election/create```.

The server will subsequently:

1. Verify that the title, description, start_date, and end_date are all valid.
2. Verify that the provided questions are all valid (no empty strings etc).
3. Verify that ``master_ballot`` was signed using ``master_ballot_signature`` and ``creator_public_key``
4. Generate ``election_public_key`` and ``election_private_key``, these are **RSA-2048** keys 
5. Generate a random **Fernet** symmetric encryption key.
6. Encrypt the random Fernet symmetric key with ``election_public_key``,
7. Insert ``master_ballot``, ``creator_public_key``, ``master_ballot_signature``, ``election_public_key``, ``election_private_key``, and ``election_encrypted_fernet_key`` into the active **BackendIO** object
8. Return ``httpcode.ELECTION_CREATED_SUCCESSFULLY`` to indicate that the election was successfully created.

When a user casts a vote in the election, their vote is encrypted using the randomly generated Fernet symmetric encryption key. It's stored in the ballot encrypted.

Anyone can download the ``election_public_key`` throughout the length of the election, but the ``election_private_key`` will remain secret until the server system time is past the ``end_date`` specified in the posted election creation JSON.

The Server uses the ``TimeManager`` class to determine if the ``election_private_key`` should be included or removed from ``GET`` requests to the API.

Current details:
* Election creators are not allowed to retroactively modify elections.
* Elections with identical titles are not allowed.
* All elections are public data.
* Anyone can query for an election's existence / cast a single vote in it.
* The results of the election are not revealed until the conclusion of the election.

## Creating a Ballot
When a user wants to vote, they must send a JSON POST request with the following format:

```
{
    "ballot": "{
        'election_title': 'The Favorite Color and Shape Election',
        'answers': '['Red', 'Triangle']'
    }",
    voter_public_key: "QPslRmynk1dtnZuhzGnMfE5XxwBOBYZb0bE3RIrZHozkUfaQHfqbmdOww2unMDa0ehOtbcmZ1dh000ODdwxDZA=="
    ballot_signature: "cArDH63/xR/mbcz7jHlRApcYsWOCdRX1UZ7jJUgc1le3vWjlcHnHcCwK5O7zfaOkZW9JnVcsW+1o+PvzDx6zeg=="

}
```

* ``ballot`` should be a JSON object in string format. It should contain the ``election_title`` and an array of ``answers`` that directly correspond to the ``questions`` in the specified election.
  * ``election_title`` should be the title of the election in UTF-8 format.
  * ``answers`` should be an array that directly corresponds to ``questions`` in the election
* ``voter_public_key`` should be a **ecdsa.SECP256k1** public key in **base64** format.
* ``ballot_signature`` should be the ``ballot`` json object in string format but signed using ``voter_public_key``'s corresponding private key.

This JSON POST should be sent to the API endpoint: ```/api/election/vote```

The server will then:
1. Verify that the provided ``voter_public_key`` can be used to decrypt the provided data.
2. Verify that this election exists
3. Verify that the actively logged in user hasn't participated in this election already.
4. Verify that all the answers are valid choices for the given election.
5. Decrypt the ``election_fernet_key_encrypted`` that corresponds to this election.
6. Use the decrypted fernet key to encrypt the user's ballot.
7. Encrypt this ballot using the election's ``election_private_key``
8. Generate a ``voter_uuid``
9. Insert the ``voter_uuid``+ all ballot data into the active BackendIO
10. Return the ``voter_uuid`` to the user so they can retrieve it again later.


Ballot Details:
* The ``voter_uuid`` is returned to the user to avoid tying them directly to a specific user.
    * If a backend database / storage mechanism is leaked attackers will only know which elections a user voter in, but not how they voted.
* Users are responsible for creating their own public private key pairs. We abstract this away for users by generating it on the client side using JavaScript + requesting that they take a picture of a QR code. The QR Code will contain their:
    * Voter UUID
    * Public Key
    * Private Key

## Strengths of System
* If a user signs data with their own private key they get immediate feedback if the server tampers with their vote at all.
* QR Codes allow the system to work on any modern web browser without requiring that users download and install a separate application.
* The system supports multiple storage backends, SQLite3 + Hyperledger support are both included but the system could easily be extended to support other storage backends with minimal effort.
* When using a blockchain based backend like Hyperledger, an immutable ledger of casted votes provides extra security as the entire history of transactions is visible, providing a strong incentive for the server to not tamper with any data prior to storage on the blockchain.

## Weaknesses of System
* Statefarm requested that all voting requests / transactions are funneled through a single central authority that can always be trusted. We designed the system according to their requirement but it has the following drawbacks if the central authority is malicious:
    * The central authority could forward any voter's public voting data elsewhere prior
    to saving it on the backend. It's impossible to verify data prior to encrypting it so this
    can't be worked around trivially (Zero Knowledge Proofs + zSnarks are a potential avenue into mitigating this but they're complex to work with.)
    * The central authority could modify your vote, generate a new public private key pair, sign the data with the new private key, throw it away, and then store the new public key on the database. When the user attempts to reverify they would get a mismatch. The user would know that their vote was discarded but the server could claim that the user simply lost their private key.
    * The central authority could claim that someone already voted when they hadn't yet and claim that they lost their ``voter_uuid``
    * A malicious user could lie and claim that they voted but a (legitimate) server changed their ballot data to something else. The user could then claim that the server logs were fabricated. (This is a problem that is inherent in all online applications with a central point of trust)
* In summary, if the user is legitimate and the server is legitimate then the user always has **verifiable proof** that their vote was untampered with. If either the server or client claim the other is lying then their vote is effectively nullified.
    * If the user sent their vote to simultaneous independent servers instead of a central authority it could help prevent the server from lying as the user could prove that the other servers didn't tamper with their data. We don't have this type of system because **Statefarm instructed us to assume there is always one central authority** despite bringing this security issue up during meetings.
