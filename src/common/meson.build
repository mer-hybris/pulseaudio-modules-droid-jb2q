libdroid_util_sources = [
  'config-parser-legacy.c',
  'config-parser-xml.c',
  'conversion.c',
  'droid-config.c',
  'droid-util.c',
  'droid-util-audio.h',
  'droid-util-41qc.h',
]

libdroid_util_headers = [
  'include/droid/conversion.h',
  'include/droid/droid-config.h',
  'include/droid/droid-util.h',
  'include/droid/version.h',
]

libdroid_util_deps = [
  droid_headers_dep,
  hybris_dep,
  hybris_common_dep,
  ltdl_dep,
  pulsecore_dep,
]

if get_option('xml')
  libdroid_util_deps += [expat_dep]
endif

install_headers(libdroid_util_headers, subdir : 'pulsecore/modules/droid')

libdroid_util = library('droid-util',
  libdroid_util_sources,
  c_args : [pa_c_args, '-DPULSEAUDIO_VERSION=@0@'.format(pa_version_major)],
  dependencies : libdroid_util_deps,
  pic : true,
  include_directories : [configinc, include_directories('include')],
  install : true,
  install_dir : modlibexecdir,
  install_rpath : rpath_dirs,
)

libdroid_util_dep = declare_dependency(
  link_with : libdroid_util,
  compile_args : pa_c_args + ['-DPULSEAUDIO_VERSION=@0@'.format(pa_version_major)],
  dependencies : libdroid_util_deps,
  include_directories : [configinc, include_directories('include')],
)

# pkgconfig
pc_cdata = configuration_data()

pc_cdata.set('prefix', get_option('prefix'))
pc_cdata.set('libdir', libdir)
pc_cdata.set('libexecdir', get_option('libexecdir'))
pc_cdata.set('PA_MAJORMINOR', pa_version_major_minor)
pc_cdata.set('PA_MODULE_VERSION', pa_version_module)

configure_file(
  input : 'libdroid-util.pc.in',
  output : 'libdroid-util.pc',
  configuration : pc_cdata,
  install_dir : join_paths(libdir, 'pkgconfig')
)
