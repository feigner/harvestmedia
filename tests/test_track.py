
# -*- coding: utf-8 -*-
from nose.tools import raises, with_setup
from unittest.case import SkipTest
from urllib2 import urlopen
import xml.etree.cElementTree as ET
import StringIO

import mock
import datetime, hashlib

from setup import init_client

import harvestmedia.api.exceptions
import harvestmedia.api.config
import harvestmedia.api.client
from harvestmedia.api.track import Track

api_key = '12345'
webservice_url = 'https://service.harvestmedia.net/HMP-WS.svc'

class HTTPResponseMock(object):

    @property
    def status(self):
        return 200

    def read(self):
        return self.read_response

@with_setup(init_client)
def test_track_dict():
    track_id = '17376d36f309f18d'
    track_xml = ET.fromstring("""<track tracknumber="1" time="02:50" lengthseconds="170" comment="Make sure you’re down the front for this fiery Post Punk workout." composer="&quot;S. Milton, J. Wygens&quot;" publisher="" name="Guerilla Pop" albumid="1c5f47572d9152f3" id="%(track_id)s" keywords="" displaytitle="Guerilla Pop" genre="Pop / Rock" tempo="" instrumentation="" bpm="" mixout="" frequency="44100" bitrate="1411" dateingested="2008-05-15 06:08:18"/>""" % locals())

    track = Track(track_xml)
    track_dict = track.as_dict()
    assert track_dict['id'] == track_id

@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_tracks_get_by_id(HTTPMock):
    track_id = '17376d36f309f18d'
    track_name = 'Guerilla Pop'

    return_values = [
            """<responsetracks>
                <tracks>
                <track tracknumber="1" time="02:50" lengthseconds="170" comment="Make sure you’re down the front for this fiery Post Punk workout." composer="&quot;S. Milton, J. Wygens&quot;" publisher="" name="%(track_name)s" albumid="1111001010001aaabeb" id="17376d36f309f18d" keywords="" displaytitle="Guerilla Pop" genre="Pop / Rock" tempo="" instrumentation="" bpm="" mixout="" frequency="44100" bitrate="1411" dateingested="2008-05-15 06:08:18">
                    <categories>
                      <category name="Tuning" id="07615de0da9a3d50">
                        <attributes>
                          <attribute name="Energy" id="a7cc2fe1b4075e51">
                            <attributes>
                              <attribute name="4" In="" Motion=""
                              id="97fda140bf94f8ca" />
                            </attributes>
                          </attribute>
                          <attribute name="Genetics" id="a5306d79fa80d3da">
                            <attributes>
                              <attribute name="3" Blended="" id="387b65044f597b48" />
                            </attributes>
                          </attribute>
                          <attribute name="Mood" id="05c1d9f5bb63b113">
                            <attributes>
                              <attribute name="1" id="527d6c887023f4ee" />
                            </attributes>
                          </attribute>
                          <attribute name="Tempo" id="65ea5898a4549788">
                            <attributes>
                              <attribute name="3" Medium="" id="b7f9cd0ca260b61a" />
                            </attributes>
                          </attribute>
                          <attribute name="Tone" id="22aadd9f2935aabe">
                            <attributes>
                              <attribute name="2" Leaning="" Dark=""
                              id="aa9c33fef3c5756f" />
                            </attributes>
                          </attribute>
                          <attribute name="Vocals" id="ea584a3d9b4fb116">
                            <attributes>
                              <attribute name="0" id="da2362b0e30b131f" />
                            </attributes>
                          </attribute>
                        </attributes>
                      </category>
                      <category name="Instrumentation" id="7907138b683424f4">
                        <attributes>
                          <attribute name="Guitars" id="abf2d935cb4182b7">
                            <attributes>
                              <attribute name="Electric" Distorted=""
                              id="96d809f485c198d4" />
                            </attributes>
                          </attribute>
                          <attribute name="Bass" id="080a1841ed350bbb">
                            <attributes>
                              <attribute name="Electric" id="a4fc0c1d3ad2cd64" />
                            </attributes>
                          </attribute>
                          <attribute name="Drums" id="16fd25d513dce9dd">
                            <attributes>
                              <attribute name="Live" id="35babb65b41e2028" />
                            </attributes>
                          </attribute>
                          <attribute name="Percussion" id="aa2850c4d1579d12">
                            <attributes>
                              <attribute name="Electronic" id="29aefdd818757ea3" />
                            </attributes>
                          </attribute>
                          <attribute name="Keyboards" id="660d379e9f7a6faf">
                            <attributes>
                              <attribute name="Synth" id="61454b4396a1f362" />
                            </attributes>
                          </attribute>
                        </attributes>
                      </category>
                    </categories>
                </track>
            </tracks>
        </responsetracks>""" % locals(),]

    def side_effect(*args):
        mock_response = StringIO.StringIO(return_values.pop(0))
        mock_response.status = 200
        return mock_response
                        
    http = HTTPMock()
    http.getresponse.side_effect = side_effect
 
    track = Track.get_by_id(track_id)

    assert track.id == track_id
    assert track.name == track_name

@with_setup(init_client)
@mock.patch('harvestmedia.api.client.httplib.HTTPSConnection')
def test_get_waveform_url(HTTPMock):
    waveform_url = "http://asset.harvestmedia.net/waveform/8185d768cd8fcaa7/{id}/{width}/{height}"
    width = 200
    height = 300
    http = HTTPMock()
    return_values = [
                     """<?xml version="1.0" encoding="utf-8"?>
                        <responseserviceinfo>
                            <asseturl
                                albumart="http://asset.harvestmedia.net/albumart/8185d768cd8fcaa7/{id}/{width}/{height}" 
                                waveform="%(waveform_url)s"
                                trackstream="http://asset.harvestmedia.net/trackstream/8185d768cd8fcaa7/{id}" 
                                trackdownload=" http://asset.harvestmedia.net/trackdownload/8185d768cd8fcaa7/{id}/{trackformat}" /> 
                            <trackformats>
                              <trackformat identifier="8185d768cd8fcaa7" extension="mp3" bitrate="320" samplerate="48" samplesize="16" /> 
                              <trackformat identifier="768cd8fcaa8185d7" extension="wav" bitrate="1536" samplerate="48" samplesize="16" /> 
                              <trackformat identifier="7jsi8fcaa818df57" extension="aif" bitrate="1536" samplerate="48" samplesize="16" /> 
                            </trackformats>
                        </responseserviceinfo>""" % locals(),
                    ]
                        
    def side_effect(*args):
        mock_response = StringIO.StringIO(return_values.pop(0))
        mock_response.status = 200
        return mock_response

    http.getresponse.side_effect = side_effect
    
    track_id = '1c5f47572d9152f3'
    track = Track()
    track.id = track_id
    waveform_url = track.get_waveform_url(width, height)

    expected_url = waveform_url.replace('{id}', track_id).replace('{width}', str(width)).replace('{height}', str(height))
    assert waveform_url == expected_url