# -*- coding: utf-8 -*-
import datetime
import hashlib
from nose.tools import raises, with_setup
import mock
import StringIO
import textwrap
import xml.etree.cElementTree as ET

import harvestmedia.api.exceptions
from harvestmedia.api.member import Member
from harvestmedia.api.playlist import Playlist

from utils import build_http_mock, get_random_md5, init_client


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_create_playlist(HttpMock):
    client = init_client()
    test_member_id = get_random_md5()
    test_playlist_id = get_random_md5()
    test_playlist_name = 'test playlist'

    content = """<?xml version="1.0" encoding="utf-8"?>
                 <ResponsePlaylists>
                    <playlists>
                        <playlist id="%(id)s" name="%(name)s" />
                    </playlists>
                </ResponsePlaylists>""" % \
                    {'id': test_playlist_id,
                     'name': test_playlist_name}

    http = build_http_mock(HttpMock, content=content)
    playlist = Playlist.create(_client=client, member_id=test_member_id, playlist_name=test_playlist_name)

    assert playlist.id == test_playlist_id
    assert playlist.name == test_playlist_name


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_get_member_playlists(HttpMock):
    client = init_client()
    test_member_id = get_random_md5()
    username = 'testuser'
    firstname = 'Test'
    lastname = 'User'
    email = 'email@email.com'

    member_xml = ET.fromstring("""<memberaccount id="%(test_member_id)s">
                                    <username>%(username)s</username>
                                    <firstname>%(firstname)s</firstname>
                                    <lastname>%(lastname)s</lastname>
                                    <email>%(email)s</email>
                                </memberaccount>""" % {'test_member_id': test_member_id,
                                                       'username': username,
                                                       'firstname': firstname,
                                                       'lastname': lastname,
                                                       'email': email})

    member = Member.from_xml(member_xml, client)

    test_playlist_id = get_random_md5()
    test_playlist_name = 'test playlist'

    content = """<?xml version="1.0" encoding="utf-8"?>
                     <ResponsePlaylists>
                        <playlists>
                            <playlist id="%(id)s" name="%(name)s">
                                <tracks>
                                    <track tracknumber="001" time="02:50" lengthseconds="170" comment="Make sure
                                        you’re down the front for this fiery Post Punk workout."
                                        composer="&quot;S. Milton, J. Wygens&quot;" publisher="HM"
                                        name="Guerilla Pop" id="17376d36f309f18d" keywords="" lyrics=""
                                        displaytitle="Guerilla Pop" genre="Pop / Rock" tempo="" instrumentation=""
                                        bpm="" mixout="" frequency="44100" bitrate="1411" />
                                </tracks>
                            </playlist>
                        </playlists>
                    </ResponsePlaylists>""" % {'id': test_playlist_id,
                                            'name': test_playlist_name}

    http = build_http_mock(HttpMock, content=content)
    playlists = member.get_playlists()

    assert isinstance(playlists, list)

    playlist = playlists[0]

    assert playlist.id == test_playlist_id
    assert playlist.name == test_playlist_name


@raises(harvestmedia.api.exceptions.MissingParameter)
def test_create_client_missing():
    playlist = Playlist.create()


@raises(harvestmedia.api.exceptions.MissingParameter)
def test_create_member_id_missing():
    client = init_client()
    playlist = Playlist.create(_client=client)


@raises(harvestmedia.api.exceptions.MissingParameter)
def test_create_name_missing():
    client = init_client()
    test_member_id = 123
    playlist = Playlist.create(_client=client, member_id=test_member_id)


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_add_track(HttpMock):
    client = init_client()
    test_playlist_id = get_random_md5()
    track_id = get_random_md5()

    content = """<?xml version="1.0" encoding="utf-8"?>
                    <responsecode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
                        <code>OK</code>
                    </responsecode>"""

    http = build_http_mock(HttpMock, content=content)
    playlist = Playlist(_client=client)
    playlist.member_id = 123
    playlist.id = test_playlist_id
    playlist.add_track(track_id)


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_remove(HttpMock):
    client = init_client()
    test_member_id = get_random_md5()
    test_playlist_id = get_random_md5()
    test_playlist_name = 'test playlist'
    test_track_id = get_random_md5()

    return_values = [
        (200, """<?xml version="1.0" encoding="utf-8"?>
                 <ResponsePlaylists>
                    <playlists>
                        <playlist id="%(test_playlist_id)s" name="%(test_playlist_name)s">
                            <tracks>
                                <track tracknumber="001" time="02:50" lengthseconds="170" comment="Make sure you’re
                                down the front for this fiery Post Punk workout."
                                composer="&quot;S. Milton, J. Wygens&quot;" publisher="HM"
                                name="Guerilla Pop" id="%(test_track_id)s" keywords=""
                                lyrics="" displaytitle="Guerilla Pop" genre="Pop / Rock" tempo=""
                                instrumentation="" bpm="" mixout="" frequency="44100" bitrate="1411" />
                            </tracks>
                        </playlist>
                    </playlists>
                </ResponsePlaylists>""" % locals()),
        (200, """<?xml version="1.0" encoding="utf-8"?>
                 <responsecode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
                    <code>OK</code>
                 </responsecode>""",),
    ]

    http = build_http_mock(HttpMock, responses=return_values)
    member = Member(_client=client)
    member.id = test_member_id
    playlists = member.get_playlists()
    playlists[0].remove()


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_remove_track(HttpMock):
    client = init_client()
    album_id = '1c5f47572d9152f3'

    now = datetime.datetime.today().isoformat()
    test_member_id = get_random_md5()
    now = datetime.datetime.today().isoformat()
    test_playlist_id = get_random_md5()
    test_playlist_name = 'test playlist'
    track_id = '17376d36f309f18d'

    return_values = [
        (200, """<?xml version="1.0" encoding="utf-8"?>
                     <ResponsePlaylists>
                        <playlists>
                            <playlist id="%(test_playlist_id)s" name="%(test_playlist_name)s">
                                <tracks>
                                    <track tracknumber="001" time="02:50" lengthseconds="170" comment="Make
                                    sure you’re down the front for this fiery Post Punk workout."
                                    composer="&quot;S. Milton, J. Wygens&quot;" publisher="HM"
                                    name="Guerilla Pop" id="%(track_id)s" keywords="" lyrics=""
                                    displaytitle="Guerilla Pop" genre="Pop / Rock" tempo=""
                                    instrumentation="" bpm="" mixout="" frequency="44100" bitrate="1411" />
                                </tracks>
                            </playlist>
                        </playlists>
                    </ResponsePlaylists>""" % locals(),),
        (200, """<?xml version="1.0" encoding="utf-8"?>
                <responsecode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
                    <code>OK</code>
                </responsecode>"""),
    ]

    http = build_http_mock(HttpMock, responses=return_values)

    member = Member(_client=client)
    member.id = test_member_id
    playlists = member.get_playlists()
    playlists[0].remove_track(track_id)


@mock.patch('harvestmedia.api.client.httplib2.Http')
def test_playlist_update(HttpMock):
    client = init_client()
    test_member_id = get_random_md5()
    test_playlist_id = get_random_md5()
    test_playlist_name = 'test playlist'
    test_playlist_update_name = 'test playlist update'
    track_id = '17376d36f309f18d'

    return_values = [
        (200, """<?xml version="1.0" encoding="utf-8"?>
                 <ResponsePlaylists>
                    <playlists>
                        <playlist id="%(test_playlist_id)s" name="%(test_playlist_name)s">
                            <tracks>
                                <track tracknumber="001" time="02:50" lengthseconds="170" comment="Make
                                sure you’re down the front for this fiery Post Punk workout."
                                composer="&quot;S. Milton, J. Wygens&quot;" publisher="HM"
                                name="Guerilla Pop" id="%(track_id)s" keywords="" lyrics=""
                                displaytitle="Guerilla Pop" genre="Pop / Rock" tempo=""
                                instrumentation="" bpm="" mixout="" frequency="44100" bitrate="1411" />
                            </tracks>
                        </playlist>
                    </playlists>
                </ResponsePlaylists>""" % locals()),
        (200, """<?xml version="1.0" encoding="utf-8"?>
                 <responsecode xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
                     <code>OK</code>
                 </responsecode>"""),
    ]

    http = build_http_mock(HttpMock, responses=return_values)

    member = Member(_client=client)
    member.id = test_member_id
    playlists = member.get_playlists()
    playlist = playlists[0]

    playlist.name = test_playlist_update_name
    playlist.update()
    assert playlist.name == test_playlist_update_name


@raises(harvestmedia.api.exceptions.MissingParameter)
def test_playlist_update_missing_member_id():
    client = init_client()
    test_playlist_name = 'test playlist'
    playlist = Playlist.create(playlist_name=test_playlist_name, _client=client)


@raises(harvestmedia.api.exceptions.MissingParameter)
def test_playlist_update_missing_playlist_name():
    client = init_client()
    test_member_id = get_random_md5()
    playlist = Playlist.create(member_id=test_member_id, _client=client)
