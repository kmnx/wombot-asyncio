#!/usr/bin/liquidsoap -v


# Put the log file in some directory where
# you have permission to write.
set("log.file.path","/tmp/<script>.log")
# Print log messages to the console,
# can also be done by passing the -v option to liquidsoap.
set("log.stdout", true)
# Use the telnet server for requests
set("server.telnet", true)


set("harbor.bind_addr","0.0.0.0")
live = input.harbor("live",port=8080,password="hackme")
jukebox = input.harbor("jukebox",port=8081,password="hackme")
#output.dummy(fallible=true, jukebox)

security = single("~/Silence.mp3")

def crossfadeOn(a,b)
  add(normalize=true,
      [ sequence([ blank(duration=2.),
        fade.initial(duration=5.,b) ]),
        fade.final(duration=5.,a) ])
end

def crossfadeOff(a,b)
  a = eat_blank(a)
  add(normalize=false,
      [ sequence([fade.initial(duration=5.,b) ]),
        fade.final(duration=5.,a) ])
end

#day     = playlist("~/radio/day.pls")
#night   = playlist("~/radio/night.pls")
#jingles = playlist("~/radio/jingles.pls")

#clock   = single("~/radio/clock.ogg")
#start   = single("~/radio/live_start.ogg")
#stop    = single("~/radio/live_stop.ogg")

# Play user requests if there are any,
# otherwise one of our playlists,
# and the default file if anything goes wrong.
# radio = fallback([ request.queue(id="request"),
#                    switch([({ 6h-22h }, day),
#                            ({ 22h-6h }, night)]),
#                    default])
# Add the normal jingles
#radio = random(weights=[1,5],[ jingles, radio ])
# And the clock jingle
#radio = add([radio, switch([({0m0s},clock)])])

#stream = fallback([live,security])

stream = fallback(track_sensitive=false, transitions=[crossfadeOn, crossfadeOff],
                 [live,security])

stream2 = fallback(track_sensitive=false, transitions=[crossfadeOn, crossfadeOff],[jukebox,security])

# Output the full stream in MP3
output.icecast(%mp3(bitrate=320, samplerate=44100, stereo=true), 
  host="localhost",port=8000,password="tiger",
  mount="stream",stream)

output.icecast(%mp3(bitrate=320, samplerate=44100, stereo=true), 
  host="localhost",port=8001,password="tiger",
  mount="stream2",stream2)
