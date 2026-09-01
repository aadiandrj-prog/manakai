from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db_models import Conversation, ConversationMessage


class ConversationRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, language: str = "en") -> Conversation:
        item = Conversation(id=f"conversation-{uuid4().hex}", detected_language=language)
        self.session.add(item)
        self.session.commit()
        return item

    def get(self, conversation_id: str) -> Conversation | None:
        return self.session.get(Conversation, conversation_id)

    def messages(self, conversation_id: str, limit: int = 12) -> list[ConversationMessage]:
        statement = select(ConversationMessage).where(ConversationMessage.conversation_id == conversation_id).order_by(ConversationMessage.created_at.desc()).limit(limit)
        return list(reversed(list(self.session.scalars(statement))))

    def add_message(self, conversation_id: str, role: str, content: str, language: str, metadata: dict | None = None) -> ConversationMessage:
        item = ConversationMessage(
            id=f"message-{uuid4().hex}", conversation_id=conversation_id, role=role,
            content=content, language=language, metadata_json=metadata or {},
        )
        self.session.add(item)
        self.session.flush()
        return item
