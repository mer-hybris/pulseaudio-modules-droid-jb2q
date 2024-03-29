PulseAudio Droid modules jb2q
=============================

For **Android 11+** modules see [pulseaudio-modules-droid](https://github.com/mer-hybris/pulseaudio-modules-droid).

Building of droid modules is split to two packages
* **common** (and **common-devel**) which contains shared library code for use in
  PulseAudio modules in this package and for inclusion in other projects
* **droid** with actual PulseAudio modules

Linking to libdroid is **not encouraged**, usually only HAL functions are needed
which can be accessed using the pulsecore shared API (see below).

Supported Android versions:

* 4.1.x with Qualcomm extensions (tested with 4.1.2)
* 4.2.x
* 4.4.x
* 5.x
* 6.0.x
* 7.x
* 8.x
* 9.x
* 10.x

Headers for defining devices and strings for different droid versions are in
src/common/droid-util-audio.h (legacy headers for Jolla 1 in droid-util-41qc.h).

When new devices with relevant new enums appear, add enum check to meson.build.
Meson build will create macros HAVE_ENUM_FOO, STRING_ENTRY_IF_FOO
and FANCY_ENTRY_IF_FOO if enum FOO exists in HAL audio.h.

For example:

    # configure.ac:
    CC_CHECK_DROID_ENUM([${DROIDHEADERS_CFLAGS}], [AUDIO_DEVICE_OUT_IP])
    CC_CHECK_DROID_ENUM([${DROIDHEADERS_CFLAGS}], [AUDIO_DEVICE_OUT_OTHER_NEW])

    # and then in droid-util-audio.h add macros to proper tables:
    /* string_conversion_table_output_device[] */
    STRING_ENTRY_IF_OUT_IP
    STRING_ENTRY_IF_OUT_OTHER_NEW

    /* string_conversion_table_output_device_fancy[] */
    FANCY_ENTRY_IF_OUT_IP("output-ip")
    FANCY_ENTRY_IF_OUT_OTHER_NEW("output-other_new")

In addition to the above macros there are also now defines
HAVE_ENUM_AUDIO_DEVICE_OUT_IP and HAVE_ENUM_AUDIO_DEVICE_OUT_OTHER_NEW.

The purpose of droid-modules is to "replace AudioFlinger". Many hardware
adaptations use ALSA as the kernel interface, but there is no saying that
someday vendor would create and use something proprietary or otherwise
different from ALSA. Also the ALSA implementation in droid devices may contain
funny ways to achieve things (notable example is voicecall) which might be
difficult to do if interfacing directly with ALSA to replace AudioFlinger.
Also using ALSA directly would mean that the whole HAL adaptation would need to
be ported for each new device adaptation. With droid-modules this is much more
simpler, with somewhat stable HAL (HALv3 as of now, also different vendors add
their own incompatible extensions) API. In best scenarios using droid-modules
with new device is just compiling against target.

Components
==========

common
------

The common part of PulseAudio Droid modules contains library for handling
most operations towards audio HAL.

### Audio policy configuration parsing

To populate our configuration structs there exists two parsers, legacy parser
for old .conf format present in Android versions 7.0 and older and new xml
format present from version 7.0 upwards. The legacy format is obsoleted in
version 7.0 but by default still in use and most 7.0 adaptations probably
contain the legacy format. But 8.0 adaptations and up start to include only
the new style xml format configuration files.

### Configuration files

By default new style xml format is tried first and if it is not found old
config is read next. If the configuration is in non-default location for
some reason "config" module argument (available for all modules, card, sink,
and source) can be used to point to the configuration file location.

By default files are tried in following order,

    /odm/etc/audio_policy_configuration.xml           (new xml format)
    /vendor/etc/audio/audio_policy_configuration.xml  (new xml format)
    /vendor/etc/audio_policy_configuration.xml        (new xml format)
    /vendor/etc/audio_policy.conf                     (legacy format)
    /system/etc/audio_policy_configuration.xml        (new xml format)
    /system/etc/audio_policy.conf                     (legacy format)

module-droid-card
-----------------

Ideally only module-droid-card is loaded and then droid-card loads
configuration, creates profiles and loads sinks and sources based on the
selected profile.

default profile
---------------

When module-droid-card is loaded with default arguments, droid-card will try
to create a default profile (called surprisingly "default"). The default
profile will try to merge useful output and input streams to one profile,
to allow use of possible low latency or deep buffer outputs.

For example configuration with

    audio_hw_modules {
        primary {
            outputs {
                primary {}
                deep_buffer {}
            }
            inputs {
                primary {}
                voice_rx {}
            }
        }
        other {
            ...
        }
    }

The default profile would contain two sinks, sink.primary and sink.deep_buffer
and one source, source.droid.

Usually this default profile is everything that is needed in normal use, and
additional profiles created should be needed only for testing things out etc.

virtual profiles
----------------

In addition to aforementioned card profiles, droid-card creates some additional
virtual profiles. These virtual profiles are used when enabling voicecall
routings etc. When virtual profile is enabled, possible sinks and sources
previously active profile had are not removed.

As an illustration, following command line sequence enables voicecall mode and
routes audio to internal handsfree (ihf - "handsfree speaker"):

(Before starting, droid_card.primary is using profile primary-primary and
sink.primary port output-speaker)

    pactl set-card-profile droid_card.primary voicecall
    pactl set-sink-port sink.primary output-parking
    pactl set-sink-port sink.primary output-speaker

After this, when there is an active voicecall (created by ofono for example),
voice audio starts to flow between modem and audio chip.

To disable voicecall and return to media audio:

    pactl set-card-profile droid_card.primary primary-primary
    pactl set-sink-port sink.primary output-parking
    pactl set-sink-port sink.primary output-speaker

With this example sequence sinks and sources are the ones from primary-primary
card profile, and they are maintained for the whole duration of the voicecall
and after.

This sequence follows the droid HAL idea that when changing audio mode the mode
change is done when next routing change happens. output-parking and
input-parking ports are just convenience for PulseAudio, where setting already
active port is a no-op (output/input-parking doesn't do any real routing
changes).

Current virtual profiles are:
* voicecall
* voicecall-record
* communication
* ringtone

Communication profile is used for VoIP-like applications, to enable some
voicecall related algorithms without being in voicecall. Ringtone profile
should be used when ringtone is playing, to again enable possible loudness
related optimizations etc. Voicecall-record profile can be enabled when
voicecall profile is active.

debugging profiles
------------------

If needed in favour of default profile one can opt to creating combinations
of all output and input definitions in a module definition. This can be
done by passing "default=false" to module-droid-card. Module argument
module_id will then defines which module to load (by default "primary").
Without default profile all input and output definitions are translated
to PulseAudio card profiles. For example configuration with

    audio_hw_modules {
        primary {
            outputs {
                primary {}
                lpa {}
            }
            inputs {
                primary {}
            }
        }
        other {
            ...
        }
    }

Would map to card profiles ([output]-[input]) primary-primary and lpa-primary.

module-droid-sink and module-droid-source
-----------------------------------------

Normally user should not need to load droid-sink or droid-source modules by
hand, but droid-card loads appropriate modules based on the active card
profile.

Output and input ports for droid-sink and droid-source are generated from the
audio_policy_configuration.xml (where available) or audio_policy.conf (legacy),
where each device generates (usually) one port, for example:

    audio_hw_modules {
        primary {
            outputs {
                primary {
                    devices = AUDIO_DEVICE_OUT_SPEAKER|AUDIO_DEVICE_OUT_EARPIECE|AUDIO_DEVICE_OUT_WIRED_HEADPHONE
                    }
                lpa {}
            }
            inputs {
                primary {
                    devices = AUDIO_DEVICE_IN_BUILTIN_MIC
                    }
            }
        }
    }

Would create following ports for sink.primary:
 * output-speaker
 * output-earpiece
 * output-wired_headphone
 * output-speaker+wired_headphone

And for source.primary:
 * input-builtin_mic

Only exception to one device one port rule is if output device list has both
OUT_SPEAKER and OUT_WIRED_HEADPHONE, then one additional combination port is
generated. How the devices are called in sink and source ports are defined in
droid-util-XXX.h

Changing output routing is then as simple as

    pactl set-sink-port sink.primary output-wired_headphone

Sink or source do not track possible headphone/other wired accessory plugging,
but this needs to be handled elsewhere and then that other entity needs to
control sinks and sources. (For example in SailfishOS this entity is OHM with
accessory-plugin and pulseaudio-policy-enforcement module for actually making
the port switching)

Droid source automatic reconfiguration
--------------------------------------

As droid HAL makes assumptions on (input) routing based on what the parameters
for the stream are (device, sample rate, channels, format, etc.) normal
PulseAudio sources are a bit inflexible as only sample rate can change after
source creation and even then there are restrictions based on alternative
sample rate value.

To overcome this and to allow some more variables affecting the stream being
passed to the input stream droid source is modified to reconfigure itself
with the source-output that connects to it. This means, that just looking at
inactive source from "pactl list" listing doesn't tell the whole story.

Droid source is always reconfigured with the *last* source-output that
connects to it, possibly already connected source-outputs will continue
to read from the source but through resampler.

For example,

1) source-output 44100Hz, stereo connects (so1)
    1) source is configured with 44100Hz, stereo
    2) so1 connects to the source without resampler
2) source-output 16000Hz, mono connects (so2)
    1) so1 is detached from the source
    2) source is configured with 16000Hz, mono
    3) so2 connects to the source without resampler
    4) resampler is created for so1, 16000Hz, mono -> 44100Hz stereo
    5) so1 is re-attached to the source through resampler
3) source-output 16000Hz, mono connects (so3)
    1) so1 and so2 are detached from the source
    2) so3 connects to the source without resampler
    3) so1 is re-attached to the source through resampler
    4) so2 is attached to the source

Classifying sinks and sources
-----------------------------

Certain property values are set to all active sinks and sources based on their
functionality to ease device classification.

Currently following properties are set:

* For droid sinks
    * droid.output.primary
    * droid.output.low_latency
    * droid.output.media_latency
    * droid.output.offload
* For droid sources
    * droid.input.builtin
    * droid.input.external

If the property is set and with value "true", the sink or source should be
used for the property type. If the property is not defined or contains
value "false" it shouldn't be used for the property type.

For example, we might have sink.primary and sink.low_latency with following
properties:

* sink.primary
    * droid.output.primary "true"
    * droid.output.media_latency "true"
* sink.low_latency
    * droid.output.low_latency "true"

There also may be just one sink, with all the properties defined as "true"
and so on.

Right now there exists only one source (input device) which will always have
both properties as true.

Quirks
------

There are some adaptations that require hacks to get things working. These
hacks can be enabled or disabled with module argument "quirks". Some quirks
are enabled by default with some adaptations etc.

Currently there are following quirks:

* input_atoi
    * Enabled by default with Android versions 5 and up.
    * Due to how atoi works in bionic vs libc we need to pass the input
      route a bit funny. If input routing doesn't work switch this on or off.
* set_parameters
    * Disabled by default.
    * Some adaptations need to use hw module's generic set_parameters call
      to change input routing. If input routing doesn't work switch this
      on or off. (mostly just older adaptations)
* close_input
    * Enabled by default.
    * Close input stream when not in use instead of suspending the stream.
      Cannot be changed when multiple inputs are merged to single source.
* unload_no_close
    * Disabled by default.
    * Don't call audio_hw_device_close() for the hw module when unloading.
      Mostly useful for tracking module unload issues.
* no_hw_volume
    * Disabled by default.
    * Some broken implementations are incorrectly probed for supporting hw
      volume control. This is manifested by always full volume with volume
      control not affecting volume level. To fix this enable this quirk.
* output_make_writable
    * Disabled by default.
    * Some implementations modify write buffer in-place when this should
      not be done. This can result in random segfaults when playing audio.
      As a workaround make the buffer memchunk writable before passing to
      audio HAL.
* realcall
    * Disabled by default.
    * Some vendors apply custom realcall parameter to HAL device when
      doing voicecall routing. If there is no voicecall audio you can
      try enabling this quirk so that the realcall parameter is applied
      when switching to voicecall profile.
* unload_call_exit
    * Disabled by default.
    * Some HAL module implementations get stuck in mutex or segfault when
      trying to unload the module. To avoid confusing segfaults call
      exit(0) instead of calling unload for the module.
* output_fast
    * Enabled by default.
    * Create separate sink if AUDIO_OUTPUT_FLAG_FAST is found. If this sink
      is misbehaving try disabling this quirk.
* output_deep_buffer
    * Enabled by default.
    * Create separate sink if AUDIO_OUTPUT_FLAG_DEEP_BUFFER is found. If
      this sink is misbehaving try disabling this quirk.
* audio_cal_wait
    * Disabled by default.
    * Certain devices do audio calibration during hw module open and
      writing audio too early will break the calibration. In these cases
      this quirk can be enabled and 10 seconds of sleep is added after
      opening hw module.
* standby_set_route
    * Disabled by default.
    * Some devices don't like to receive set_parameters() call while they
      are in write(), even if it seems the mutexes are correctly in place.
      Standby is another synchronization point which seems to work better.
      If there are hiccups like long delays when setting route during
      voice call start try enabling this quirk.
* speaker_before_voice
    * Disabled by default.
    * Set route to speaker before changing audio mode to AUDIO_MODE_IN_CALL.
      Some devices don't get routing right if the route is something else
      (like AUDIO_DEVICE_OUT_WIRED_HEADSET) before calling set_mode().
      If routing is wrong when call starts with wired accessory connected
      try enabling this quirk.

For example, to disable input_atoi and enable close_input quirks, use module
argument

    quirks=-input_atoi,+close_input

Volume control during voicecall
-------------------------------

When voicecall virtual profile is enabled, active droid-sink is internally
switched to voicecall volume control mode. What this means is changing the sink
volume or volume of normal streams connected to the sink do not change active
voicecall volume. Special stream is needed to control the voicecall volume
level. By default this stream is identified by stream property media.role,
with value "phone". This can be changed by providing module arguments
voice_property_key and voice_property_value to module-droid-card.

Usually droid HAL has 6 volume levels for voicecall.

Temporary sink audio routing
----------------------------

It is possible to add temporary route to sink audio routing with specific
stream property. When stream with property key
droid.device.additional-route connects to droid-sink, this extra route is set
(if possible) as the enabled route for the duration of the stream.

For example, if droid-sink has active port output-wired_headphone:

    paplay --property=droid.device.additional-route=AUDIO_DEVICE_OUT_SPEAKER a.wav

As long as the new stream is connected to droid-sink, output routing is
SPEAKER.

HAL API
-------

If there is need to call HAL directly from other modules it can be done with
function pointer API stored in PulseAudio shared map.

Once the function pointers are acquired when called they will work the same
way as defined in Android audio.h. For example:

    void   *handle;
    int   (*set_parameters)(void *handle, const char *key_value_pairs);
    char* (*get_parameters)(void *handle, const char *keys);

    handle = pa_shared_get(core, "droid.handle.v1");
    set_parameters = pa_shared_get(core, "droid.set_parameters.v1");
    get_parameters = pa_shared_get(core, "droid.get_parameters.v1");

    set_parameters(handle, "route=2;");
    char *value = get_parameters(handle, "connected");

module-droid-keepalive
----------------------

Module relocated to its own package pulseaudio-module-keepalive.
