# -*- coding: utf-8 -*-
import DB
from TTSSilero import Speakers


class SpeakersSettingsAdapterDiscord:
    DEFAULT_SPEAKER = Speakers.kseniya

    def get_speaker(self, guild_id: int, user_id: int) -> Speakers:
        user_defined_speaker = self.get_speaker_user(guild_id, user_id)
        if user_defined_speaker is None:
            return self.get_speaker_global(guild_id)

        else:
            return user_defined_speaker

    def get_speaker_global(self, guild_id: int) -> Speakers:
        server_speaker_query = DB.ServerSpeaker.select()\
            .where(DB.ServerSpeaker.server_id == guild_id)

        if server_speaker_query.count() == 1:
            return Speakers(server_speaker_query.get().speaker)

        else:
            return self.DEFAULT_SPEAKER

    def get_speaker_user(self, guild_id: int, user_id: int) -> Speakers | None:
        user_speaker_query = DB.UserServerSpeaker.select()\
            .where(DB.UserServerSpeaker.server_id == guild_id)\
            .where(DB.UserServerSpeaker.user_id == user_id)

        if user_speaker_query.count() == 1:
            return Speakers(user_speaker_query.get().speaker)

        else:
            return None

    @property
    def available_speakers(self) -> set[str]:
        return {speaker.name for speaker in Speakers}

    def set_speaker_user(self, guild_id: int, user_id: int, speaker: Speakers) -> None:
        DB.UserServerSpeaker.replace(server_id=guild_id, user_id=user_id, speaker=speaker.value).execute()

    def set_speaker_global(self, guild_id: int, speaker: Speakers) -> None:
        DB.ServerSpeaker.replace(server_id=guild_id, speaker=speaker.value).execute()


speakers_settings_adapter = SpeakersSettingsAdapterDiscord()
