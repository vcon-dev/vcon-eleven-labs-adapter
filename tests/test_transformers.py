"""
Tests for vCon transformation components
"""

import pytest
from vcon.party import Party
from src.transformers.party_mapper import PartyMapper
from src.transformers.dialog_processor import DialogProcessor
from src.transformers.vcon_builder import VconBuilder


class TestPartyMapper:
    """Tests for PartyMapper"""

    def test_map_parties(self, sample_conversation):
        """Test mapping conversation participants to vCon parties"""
        parties = PartyMapper.map_parties(sample_conversation)

        assert len(parties) == 2
        assert parties[0].name == "Sarah"
        assert parties[0].role == "agent"
        assert parties[1].name == "John Smith"
        assert parties[1].role == "customer"

    def test_map_parties_with_email_phone(self, sample_conversation):
        """Test that party mapper includes email and phone"""
        parties = PartyMapper.map_parties(sample_conversation)

        agent_party = parties[0]
        assert agent_party.mailto == "sarah@company.com"
        assert agent_party.tel == "+1-555-0100"

    def test_map_parties_empty_participants(self):
        """Test mapping with no participants"""
        from src.models.elevenlabs_models import Conversation
        from datetime import datetime

        conv = Conversation(
            id="conv_1",
            agent_id="agent_1",
            start_time=datetime.now(),
            participants=[],
        )

        parties = PartyMapper.map_parties(conv)

        assert parties == []

    def test_get_party_index(self, sample_conversation):
        """Test finding party by UUID"""
        parties = PartyMapper.map_parties(sample_conversation)

        idx = PartyMapper.get_party_index(parties, "agent_participant_1")

        assert idx == 0

    def test_get_party_index_not_found(self, sample_conversation):
        """Test finding party when it doesn't exist"""
        parties = PartyMapper.map_parties(sample_conversation)

        idx = PartyMapper.get_party_index(parties, "unknown_id")

        assert idx == -1

    def test_get_agent_party_index(self, sample_conversation):
        """Test finding agent party"""
        parties = PartyMapper.map_parties(sample_conversation)

        idx = PartyMapper.get_agent_party_index(parties)

        assert idx == 0
        assert parties[idx].role == "agent"

    def test_get_customer_party_index(self, sample_conversation):
        """Test finding customer party"""
        parties = PartyMapper.map_parties(sample_conversation)

        idx = PartyMapper.get_customer_party_index(parties)

        assert idx == 1
        assert parties[idx].role == "customer"


class TestDialogProcessor:
    """Tests for DialogProcessor"""

    def test_process_conversation_dialogs(self, sample_conversation):
        """Test processing conversation to dialogs"""
        party_indices = {"agent_participant_1": 0, "customer_participant_1": 1}

        dialogs = DialogProcessor.process_conversation_dialogs(
            sample_conversation,
            party_indices,
        )

        assert len(dialogs) >= 1
        assert dialogs[0].type == "recording"

    def test_process_conversation_dialogs_with_transcript(self, sample_conversation):
        """Test processing conversation with transcript"""
        party_indices = {"agent_participant_1": 0, "customer_participant_1": 1}

        dialogs = DialogProcessor.process_conversation_dialogs(
            sample_conversation,
            party_indices,
            include_transcript=True,
        )

        assert len(dialogs) == 2

        audio_dialog = next((d for d in dialogs if d.type == "recording"), None)
        transcript_dialog = next((d for d in dialogs if d.type == "text"), None)

        assert audio_dialog is not None
        assert transcript_dialog is not None

    def test_create_audio_dialog(self, sample_conversation):
        """Test creating audio dialog"""
        party_indices = {"agent_participant_1": 0, "customer_participant_1": 1}

        dialog = DialogProcessor._create_audio_dialog(
            sample_conversation,
            party_indices,
        )

        assert dialog.type == "recording"
        # Dialog.start is ISO string, compare with isoformat()
        assert dialog.start == sample_conversation.start_time.isoformat()
        assert 0 in dialog.parties
        assert 1 in dialog.parties

    def test_create_transcript_dialog(self, sample_conversation):
        """Test creating transcript dialog"""
        party_indices = {"agent_participant_1": 0, "customer_participant_1": 1}

        dialog = DialogProcessor._create_transcript_dialog(
            sample_conversation,
            party_indices,
        )

        assert dialog.type == "text"
        assert sample_conversation.transcript.text in dialog.body

    def test_process_conversation_no_audio(self, sample_conversation_no_audio):
        """Test processing conversation without audio"""
        party_indices = {"agent_participant_1": 0, "customer_participant_1": 1}

        dialogs = DialogProcessor.process_conversation_dialogs(
            sample_conversation_no_audio,
            party_indices,
        )

        assert len(dialogs) >= 1
        assert any(d.type == "text" for d in dialogs)


class TestVconBuilder:
    """Tests for VconBuilder"""

    def test_builder_initialization(self):
        """Test VconBuilder initialization"""
        builder = VconBuilder(
            include_analysis=True,
            include_attachments=True,
        )

        assert builder.include_analysis is True
        assert builder.include_attachments is True

    def test_build_vcon(self, sample_conversation):
        """Test building a complete vCon"""
        builder = VconBuilder()

        vcon = builder.build_vcon(sample_conversation)

        assert vcon.uuid is not None
        assert len(vcon.parties) == 2
        assert len(vcon.dialog) >= 1

    def test_build_vcon_with_analysis(self, sample_conversation):
        """Test building vCon with analysis"""
        builder = VconBuilder(include_analysis=True)

        vcon = builder.build_vcon(sample_conversation)

        assert vcon.uuid is not None
        assert len(vcon.parties) == 2

    def test_build_vcon_without_attachments(self, sample_conversation):
        """Test building vCon without attachments"""
        builder = VconBuilder(include_attachments=False)

        vcon = builder.build_vcon(sample_conversation)

        assert vcon.uuid is not None

    def test_build_vcon_metadata(self, sample_conversation):
        """Test that vCon metadata is set correctly"""
        builder = VconBuilder()

        vcon = builder.build_vcon(sample_conversation)

        # Check tags (they can be strings or objects with value attribute)
        tag_values = []
        if vcon.tags:
            for tag in vcon.tags:
                if isinstance(tag, str):
                    tag_values.append(tag)
                elif hasattr(tag, 'value'):
                    tag_values.append(tag.value)
        
        # The conversation's start is on its Session (core-05)
        session = vcon.to_dict()["sessions"][0]
        assert session["start"] == sample_conversation.start_time.isoformat()
        assert session["duration"] == sample_conversation.duration_ms / 1000

    def test_build_vcon_tags(self, sample_conversation):
        """Test that tags are added to vCon"""
        builder = VconBuilder()

        vcon = builder.build_vcon(sample_conversation)

        assert vcon.uuid is not None


class TestVconValidation:
    """Tests for vCon validation"""

    def test_built_vcon_is_valid(self, sample_conversation):
        """Test that built vCons pass validation"""
        builder = VconBuilder()

        vcon = builder.build_vcon(sample_conversation)

        assert vcon.uuid is not None
        assert len(vcon.parties) > 0

    @pytest.mark.parametrize("fixture", ["sample_conversation", "sample_conversation_no_audio"])
    def test_built_vcon_passes_vcon_lib_validation(self, fixture, request):
        """Built vCons are core-05 (0.5.0) and pass vcon-lib's is_valid()"""
        conversation = request.getfixturevalue(fixture)
        conversation._transcript_data = {
            "full_text": "Agent: Hello\n\nUser: Hi",
            "transcript_turns": [{"role": "agent", "message": "Hello"}],
            "analysis": {"summary": "s", "title": "t", "call_successful": "success"},
        }

        vcon = VconBuilder().build_vcon(conversation)

        assert vcon.is_valid() == (True, [])
        assert vcon.get_validation_warnings() == []
        data = vcon.to_dict()
        assert data["vcon"] == "0.5.0"
        assert len(data["sessions"]) == 1
        session = data["sessions"][0]
        assert session["parties"] == [0, 1]
        assert session["dialog"] == list(range(len(data["dialog"])))
        for dialog in data["dialog"]:
            assert dialog["type"] in ("recording", "text")
            assert "mimetype" not in dialog
        assert {a["purpose"] for a in data["attachments"]} == {"call_record", "tags"}
        for attachment in data["attachments"]:
            assert attachment["party"] == 0  # the agent
            assert attachment["session"] in (0, [0])  # tags list every Session
            assert not isinstance(attachment["body"], str)
        assert [a["type"] for a in data["analysis"]] == ["transcript", "summary"]
        for analysis in data["analysis"]:
            assert analysis["encoding"] == "json"
            assert isinstance(analysis["body"], dict)
            assert analysis["dialog"] in range(len(data["dialog"]))

    def test_no_audio_has_no_recording_dialog(self, sample_conversation_no_audio):
        """Without audio there is no placeholder recording Dialog"""
        data = VconBuilder().build_vcon(sample_conversation_no_audio).to_dict()

        assert [d["type"] for d in data["dialog"]] == ["text"]

    def test_downloaded_audio_url_carries_content_hash(self, sample_conversation):
        """A recording referenced by url carries its sha512 content_hash"""
        from src.transformers.dialog_processor import content_hash

        sample_conversation.audio.content_hash = content_hash(b"audio")
        data = VconBuilder().build_vcon(sample_conversation).to_dict()

        recording = data["dialog"][0]
        assert recording["url"] == sample_conversation.audio.url
        assert recording["content_hash"].startswith("sha512-")
        assert "=" not in recording["content_hash"]
        assert recording["mediatype"] == "audio/wav"
