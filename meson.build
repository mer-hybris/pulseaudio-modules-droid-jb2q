project('pulseaudio-modules-droid-jb2q', 'c',
        version : run_command(find_program('git-version-gen'), join_paths(meson.current_source_dir(), '.tarball-version'), check: true).stdout().strip(),
        meson_version : '>= 0.50.0',
        default_options : [ 'c_std=gnu11' ]
        )

cc = meson.get_compiler('c')

configinc = include_directories('.')
libdir = join_paths(get_option('prefix'), get_option('libdir'))

pa_c_args = ['-DHAVE_CONFIG_H']

droiddevice = get_option('droid-device')
pa_c_args += ['-DDROID_DEVICE_@0@=1'.format(droiddevice.underscorify().to_upper())]
pa_c_args += ['-DDROID_DEVICE_STRING="@0@"'.format(droiddevice)]

# dependencies
droid_headers_dep = dependency('android-headers', required : true)
if get_option('xml')
  expat_dep = dependency('expat', version : '>= 2.1', required : true)
endif
hybris_dep = dependency('libhardware', version : '>= 0.1.0', required : true)
hybris_common_dep = cc.find_library('hybris-common', required : true)
ltdl_dep = cc.find_library('ltdl', required : true)
pulsecore_dep = dependency('pulsecore', version : '>= 14.2', required : true)

pa_version_str = meson.project_version()
# For tarballs, the first split will do nothing, but for builds in git, we
# split out suffixes when there are commits since the last tag
# (e.g.: v11.99.1-3-gad14bdb24 -> v11.99.1)
version_split = pa_version_str.split('-')[0].split('.')
pa_version_major = version_split[0].split('v')[0]
pa_version_minor = version_split[1]
pa_version_module = version_split[2].split('+')[0]
pa_version_major_minor = pa_version_major + '.' + pa_version_minor

modlibexecdir = get_option('modlibexecdir')
if modlibexecdir == ''
  modlibexecdir = join_paths(libdir, 'pulse-' + pa_version_major_minor, 'modules')
endif

privlibdir = join_paths(libdir, 'pulseaudio')
rpath_dirs = join_paths(privlibdir) + ':' + join_paths(modlibexecdir)

cdata = configuration_data()
cdata.set_quoted('PACKAGE', meson.project_name())
cdata.set_quoted('PACKAGE_NAME', meson.project_name())
cdata.set_quoted('PACKAGE_VERSION', pa_version_str)
cdata.set_quoted('VERSION', pa_version_str)

if get_option('xml')
  cdata.set('HAVE_EXPAT', 1)
endif

# Atomic operations

if get_option('atomic-arm-memory-barrier')
    cdata.set('ATOMIC_ARM_MEMORY_BARRIER_ENABLED', 1)
endif

need_libatomic_ops = false

atomictest = '''void func() {
  volatile int atomic = 2;
  __sync_bool_compare_and_swap (&atomic, 2, 3);
}
'''

if cc.compiles(atomictest)
  cdata.set('HAVE_ATOMIC_BUILTINS', 1)

  newatomictest = '''void func() {
    int c = 0;
    __atomic_store_n(&c, 4, __ATOMIC_SEQ_CST);
  }
  '''

  if(cc.compiles(newatomictest))
    cdata.set('HAVE_ATOMIC_BUILTINS_MEMORY_MODEL', 1)
  endif

elif host_machine.cpu_family() == 'arm'
  if host_machine.system() == 'linux' and get_option('atomic-arm-linux-helpers')
    cdata.set('ATOMIC_ARM_LINUX_HELPERS', 1)
  else
    armatomictest = '''int func() {
      volatile int a=0;
      int o=0, n=1, r;
      asm volatile (
          "ldrex    %0, [%1]\n"
          "subs  %0, %0, %2\n"
          "strexeq %0, %3, [%1]\n"
          : "=&r" (r)
          : "r" (&a), "Ir" (o), "r" (n)
      : "cc");
      return (a==1 ? 0 : -1);
    }
    '''

    if cc.compiles(armatomictest)
      cdata.set('ATOMIC_ARM_INLINE_ASM', 1)
    else
      need_libatomic_ops = true
    endif
  endif # arm && !linux

elif not ['freebsd', 'netbsd'].contains(host_machine.system())
  need_libatomic_ops = true
endif # !atomic helpers && !arm

if need_libatomic_ops
  assert(cc.has_header('atomic_ops.h'), 'Need libatomic_ops')

  cdata.set('AO_REQUIRE_CAS', 1)

  if host_machine.system() != 'windows'
    libatomic_ops_dep = cc.find_library('atomic_ops', required : true)
  else
    libatomic_ops_dep = dependency('', required: false)
  endif
else
  libatomic_ops_dep = dependency('', required: false)
endif

check_enums = [
# Output devices
  'AUDIO_DEVICE_OUT_HDMI',
  'AUDIO_DEVICE_OUT_HDMI_ARC',
  'AUDIO_DEVICE_OUT_TELEPHONY_TX',
  'AUDIO_DEVICE_OUT_LINE',
  'AUDIO_DEVICE_OUT_SPDIF',
  'AUDIO_DEVICE_OUT_AUX_LINE',
  'AUDIO_DEVICE_OUT_SPEAKER_SAFE',
  'AUDIO_DEVICE_OUT_FM',
  'AUDIO_DEVICE_OUT_FM_TX',
  'AUDIO_DEVICE_OUT_ANC_HEADSET',
  'AUDIO_DEVICE_OUT_ANC_HEADPHONE',
  'AUDIO_DEVICE_OUT_PROXY',
# Added in 6.0
  'AUDIO_DEVICE_OUT_IP',

# Input devices
  'AUDIO_DEVICE_IN_HDMI',
  'AUDIO_DEVICE_IN_TELEPHONY_RX',
  'AUDIO_DEVICE_IN_FM_TUNER',
  'AUDIO_DEVICE_IN_TV_TUNER',
  'AUDIO_DEVICE_IN_LINE',
  'AUDIO_DEVICE_IN_SPDIF',
  'AUDIO_DEVICE_IN_BLUETOOTH_A2DP',
  'AUDIO_DEVICE_IN_LOOPBACK',
  'AUDIO_DEVICE_IN_PROXY',
  'AUDIO_DEVICE_IN_FM_RX',
  'AUDIO_DEVICE_IN_FM_RX_A2DP',
  'AUDIO_DEVICE_IN_ALL_USB',
# Added in 6.0
  'AUDIO_DEVICE_IN_IP',

# Audio sources
  'AUDIO_SOURCE_FM_TUNER',
  'AUDIO_SOURCE_FM_RX',
  'AUDIO_SOURCE_FM_RX_A2DP',

# Output flags
  'AUDIO_OUTPUT_FLAG_COMPRESS_OFFLOAD',
  'AUDIO_OUTPUT_FLAG_NON_BLOCKING',
  'AUDIO_OUTPUT_FLAG_HW_AV_SYNC',
  'AUDIO_OUTPUT_FLAG_VOIP_RX',
  'AUDIO_OUTPUT_FLAG_INCALL_MUSIC',
  'AUDIO_OUTPUT_FLAG_COMPRESS_PASSTHROUGH',
# Added in 6.0
  'AUDIO_OUTPUT_FLAG_TTS',
  'AUDIO_OUTPUT_FLAG_RAW',
  'AUDIO_OUTPUT_FLAG_SYNC',
  'AUDIO_OUTPUT_FLAG_IEC958_NONAUDIO',

# Input flags
  'AUDIO_INPUT_FLAG_NONE',
  'AUDIO_INPUT_FLAG_FAST',
  'AUDIO_INPUT_FLAG_HW_HOTWORD',
  'AUDIO_INPUT_FLAG_RAW',
  'AUDIO_INPUT_FLAG_SYNC',
  'AUDIO_INPUT_FLAG_MMAP_NOIRQ',
  'AUDIO_INPUT_FLAG_VOIP_TX',

# Channels
  'AUDIO_CHANNEL_OUT_SURROUND',
  'AUDIO_CHANNEL_OUT_5POINT1_BACK',
  'AUDIO_CHANNEL_OUT_5POINT1_SIDE',
  'AUDIO_CHANNEL_IN_VOICE_CALL_MONO',
  'AUDIO_CHANNEL_IN_VOICE_UPLINK_MONO',
  'AUDIO_CHANNEL_IN_VOICE_DNLINK_MONO',

# Formats
  'AUDIO_FORMAT_PCM_24_BIT_PACKED',
  'AUDIO_FORMAT_PCM_OFFLOAD',
  'AUDIO_FORMAT_FLAC',
  'AUDIO_FORMAT_OPUS',
]

foreach e : check_enums
  if cc.has_header_symbol('system/audio.h', e, dependencies : droid_headers_dep, prefix : '#include <android-config.h>\n#ifdef QCOM_BSP\n#define QCOM_HARDWARE\n#endif')
    define = 'HAVE_ENUM_' + e
    cdata.set(define, 1)
    define = 'STRING_ENTRY_IF_' + e
    cdata.set(define, 'STRING_ENTRY(' + e + '),')
    define = 'FANCY_ENTRY_IF_' + e + '(n)'
    cdata.set(define, '{' + e + ', n},')
  else
    define = 'STRING_ENTRY_IF_' + e
    cdata.set(define, '')
    define = 'FANCY_ENTRY_IF_' + e + '(n)'
    cdata.set(define, '')
  endif
endforeach

# Headers
check_headers = [
  'valgrind/memcheck.h',
]

foreach h : check_headers
  if cc.has_header(h)
    define = 'HAVE_' + h.underscorify().to_upper()
    cdata.set(define, 1)
  endif
endforeach

# Now generate config.h from everything above
configure_file(output : 'config.h', configuration : cdata)

subdir('src')
