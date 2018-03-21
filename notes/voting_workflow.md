# Creating an Election:
After logging into the BallotBlock-API, if the user is an **election_creator** and
they want to create an election in the system, then they must send a JSON POST
request with the following format:

```
{
    public_key: "5a049409e2167292346f637613104d0fdb3a44ce3c41f4532b0cd6288a0a64043e552ce8e7c53fd8ebff0461a993155dab52bb60158656d8516315c03844f4a3",

    data: {
        "election_title": "Favorite Color and Shape Election",
        "description": "Pick your favorite color / shape."
        "start_date": 1521507388,
        "end_date": 1522371388,
        "questions: [
            ["Favorite Color?", ["Red", "Blue"]],
            ["Favorite Shape?", ["Square", "Triangle"]]
        ]"
    }
}
```

* Public key should be a 'ecdsa.SECP256k1' public key in hex format.
* Data should be a JSON object in string format. It should be digitally signed using the accompanying private key. The data is transparent in the above example but when sent to the server it should be encrypted using the private key.
    * This prevents the central authority from tampering with election data.
* If the election creator loses their private key the election contents can always be read.

This JSON POST should be sent to the server endpoint "/api/election/create".

The server will subsequently:

1. Verify that the provided public_key can be used to decrypt the provided data.
2. Verify that the title, description, start_date, and end_date are all valid.
3. Verify that the provided questions are all valid.
4. Generate a server public private key pair for the election,
5. Store the election + corresponding public private key pair using the active BackendIO object.

The server public-private key pair allows us to encrypt each user's ballot. This allows for preventing people from viewing the results of the election prior to its conclusion.


Current details:
* Election creators are not allowed to retroactively modify elections.
* Elections with identical titles are not allowed.
* All elections are public data.
* Anyone can query for an election's existence / cast a single vote in it.

## Creating a Ballot
When a user wants to vote, they must send a JSON POST request with the following format:

```
{
    public_key: "40fb25466ca793576d9d9ba1cc69cc7c4e57c7004e05865bd1b137448ad91e8ce451f6901dfa9b99d3b0c36ba73036b47a13ad6dc999d5d874d34383770c4364",
    data: {
        "election_title": "The Favorite Color and Shape Election",
        "answers": "['Red', 'Triangle']"
    },
}
```

* Public key should be a 'ecdsa.SECP256k1' public key in hex format.
* Data should be a JSON object in string format. It should be digitally signed using the accompanying private key. The data is transparent in the above example but when sent to the server it should be encrypted using the private key.
    * This prevents the central authority from tampering with ballot data.
* If the voter loses their private key the ballot can still be counted.

This JSON POST should be sent to the API endpoint: "/api/election/vote"

The server will then:
1. Verify that the provided public_key can be used to decrypt the provided data.
2. Verify that this election exists
3. Verify that the actively logged in user hasn't participated in this election already.
4. Verify that all the answers are valid choices for the given election.
5. Generate a voter uuid and return that to the user. The user should use this UUID if they want to look up their voter later and verify it's prescence.
6. Encrypt this ballot using the server's per election key
7. Store it on the backend using the current BackendIO object.

Ballot Details:
* The user's username isn't directly used to avoid tying a particular user to every single election in the system. They should be able to reveal their voting habits on a per-election basis if they choose. (Secret Ballot)
* Each user's ballot is signed on the client-side using the user's private key, this allows the user to verify that their vote was never tampered with.
* Each user's ballot is then encrypted on the server side using the server's public key, the data cannot be encrypted until the per election private key is revealed at the conclusion of the election.

## Strengths and Weaknesses of System
* Election creators / voters have to manage a public key, private key, and uuid to verify their votes were recorded and are present in the system.
    * We can embed all this information in a 250 byte qr code and request the user to photograph it to keep track of their election / vote details.