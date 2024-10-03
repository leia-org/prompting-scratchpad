
import shelve

from uuid import UUID, uuid4
from dataclasses import dataclass, asdict
from http import HTTPStatus

import yaml

from flask import Response, request, jsonify, render_template

from constants import CHATS_SHELF, CLIENTS_FILE, OAI_CLIENT

@dataclass
class Message:
    role: str
    content: str


@dataclass
class Chat:
    uuid: UUID
    display_name: str
    messages: list[Message]

    def get_response(self, message: str | None = None, model: str = "gpt-4o") -> str:
        if OAI_CLIENT is None:
            raise ValueError(f"Cannot get response with null API client!")

        if message is not None:
            self.messages.append(Message(
                role = "user",
                content=message
            ))

        completion = OAI_CLIENT.chat.completions.create(
            model = model,
            messages = [ asdict(msg) for msg in self.messages ]
        )

        msg = completion.choices[0].message

        self.messages.append(Message(
            role = "assistant",
            content = str(msg)
        ))

        return str(msg)

    @staticmethod
    def read() -> Response:
        """
        Input
        ------
        { 
            uuid : str
        }

        Returns
        ------
        { Chat }
        """
        if not request.is_json:
            return Response(status=HTTPStatus.BAD_REQUEST)
    
        payload = request.json
        assert payload is not None

        if "uuid" not in payload:
            return Response(
                response="Please provide field `uuid` in your request",
                status=HTTPStatus.BAD_REQUEST # 400
            )

        uuid = payload['uuid']

        with shelve.open(CHATS_SHELF) as chats:
            
            if uuid not in chats:
                return Response(
                    response="Could not find a chat with that ID!",
                    status=HTTPStatus.NOT_FOUND # 404
                )

            chat = chats[uuid]

        return jsonify(asdict(chat))

    @staticmethod
    def create() -> Response:
        """
        Create a new chat

        Input
        ------
        {  
            client: str // the display name of the client  
        }  

        Returns
        ------
        { Chat }
        """
        if not request.is_json:
            return Response(
                response="Please provide a JSON request",
                status=HTTPStatus.BAD_REQUEST
            )

        payload = request.json
        assert payload is not None

        if "client" not in payload:
            return Response(
                response="Please provide a `client` field in your request!",
                status=HTTPStatus.BAD_REQUEST
            )

        client = Client.get_one(payload['client'])
        chat = Chat(
            uuid=uuid4(),
            display_name=client.display_name,
            messages=[
                Message(
                    role="system",
                    content=render_template("client.system_prompt.jinja2", **asdict(client))
                ),
            ]
        )

        with shelve.open(CHATS_SHELF) as chats:
            chats[str(chat.uuid)] = chat

        return jsonify(asdict(chat))

    @staticmethod
    def update() -> Response:
        """
        Add a message to the chat

        Input
        ------
        {  
            uuid : str  
            user_message : str   
        }

        Returns
        ------
        { Chat }
        """
        if not request.is_json:
            return Response(status=HTTPStatus.BAD_REQUEST)
    
        payload = request.json
        assert payload is not None

        if "uuid" not in payload or \
            "user_message" not in payload:
            return Response(
                response="Please provide both a `uuid` and `user_message` in your request",
                status=HTTPStatus.BAD_REQUEST # 400
            )

        uuid = payload['uuid']

        with shelve.open(CHATS_SHELF) as chats:
            
            if uuid not in chats:
                return Response(
                    response="Could not find a chat with that ID!",
                    status=HTTPStatus.NOT_FOUND # 404
                )

            chat = chats[uuid]

        _ = chat.get_response(payload['user_message'])

        with shelve.open(CHATS_SHELF) as chats:
            chats[uuid] = chat

        return jsonify(asdict(chat))

    @staticmethod
    def delete() -> Response:
        """
        Stop tracking a chat

        Input
        ------
        { 
            uuid : str
        }

        Returns
        ------
        { Chat }
        """
        if not request.is_json:
            return Response(status=HTTPStatus.BAD_REQUEST)
    
        payload = request.json
        assert payload is not None

        if "uuid" not in payload:
            return Response(
                response="Please provide a `uuid` in your request",
                status=HTTPStatus.BAD_REQUEST # 400
            )

        uuid = payload['uuid']

        with shelve.open(CHATS_SHELF) as chats:
            
            if uuid not in chats:
                return Response(
                    response="Could not find a chat with that ID!",
                    status=HTTPStatus.NOT_FOUND # 404
                )

            chat = chats[uuid]
            del chats[uuid]

        return jsonify(asdict(chat))

@dataclass
class Client:
    display_name: str
    background: str
    needs_and_limitations: str
    difficulty: str
    output_type: str

    @staticmethod
    def get_all() -> list["Client"]:
        with open(CLIENTS_FILE, "r") as f:
            clients_raw = yaml.safe_load(f)

        clients = [
            Client(**data)
            for data in clients_raw
        ]

        return clients

    @staticmethod
    def get_one(client_name: str) -> "Client":

        matching_clients = [ c for c in Client.get_all() if c.display_name == client_name ]
        if len(matching_clients) != 1:
            raise Exception(f"Did not find exactly one matching client!: "
                            f"{[ c.display_name for c in matching_clients ]}")

        return matching_clients[0]

    @staticmethod
    def enumerate() -> Response:
        """
        Input
        ------
        { }

        Returns
        ------
        [ Client ]
        """

        return jsonify([ asdict(c) for c in Client.get_all() ])

__all__ = [
    "Chat",
    "Client"
]
