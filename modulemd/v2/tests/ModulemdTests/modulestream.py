import os
import sys
try:
    import unittest
    import gi

    gi.require_version('Modulemd', '2.0')
    from gi.repository import GLib
    from gi.repository import Modulemd
except ImportError:
    # Return error 77 to skip this test on platforms without the necessary
    # python modules
    sys.exit(77)

from base import TestBase

modulestream_versions = [
    Modulemd.ModuleStreamVersionEnum.ONE,
    Modulemd.ModuleStreamVersionEnum.TWO]


class TestModuleStream(TestBase):

    def test_constructors(self):
        for version in modulestream_versions:

            # Test that the new() function works
            stream = Modulemd.ModuleStream.new(version, 'foo', 'latest')
            assert stream
            assert isinstance(stream, Modulemd.ModuleStream)

            assert stream.props.mdversion == version
            assert stream.get_mdversion() == version
            assert stream.props.module_name == 'foo'
            assert stream.get_module_name() == 'foo'
            assert stream.props.stream_name == 'latest'
            assert stream.get_stream_name() == 'latest'

            # Test that the new() function works without a stream name
            stream = Modulemd.ModuleStream.new(version, 'foo')
            assert stream
            assert isinstance(stream, Modulemd.ModuleStream)

            assert stream.props.mdversion == version
            assert stream.get_mdversion() == version
            assert stream.props.module_name == 'foo'
            assert stream.get_module_name() == 'foo'
            assert stream.props.stream_name is None
            assert stream.get_stream_name() is None

            # Test that the new() function works with no module name
            stream = Modulemd.ModuleStream.new(version, None, 'latest')
            assert stream
            assert isinstance(stream, Modulemd.ModuleStream)

            assert stream.props.mdversion == version
            assert stream.get_mdversion() == version
            assert stream.props.module_name is None
            assert stream.get_module_name() is None
            assert stream.props.stream_name == 'latest'
            assert stream.get_stream_name() == 'latest'

            # Test that the new() function works with no module or stream
            stream = Modulemd.ModuleStream.new(version)
            assert stream
            assert isinstance(stream, Modulemd.ModuleStream)

            assert stream.props.mdversion == version
            assert stream.get_mdversion() == version
            assert stream.props.module_name is None
            assert stream.get_module_name() is None
            assert stream.props.stream_name is None
            assert stream.get_stream_name() is None

        # Test that we cannot instantiate directly
        with self.assertRaisesRegex(TypeError, 'cannot create instance of abstract'):
            Modulemd.ModuleStream()

        # Test with a zero mdversion
        with self.assertRaisesRegex(TypeError, 'constructor returned NULL'):
            with self.expect_signal():
                defs = Modulemd.ModuleStream.new(0)

        # Test with an unknown mdversion
        with self.assertRaisesRegex(TypeError, 'constructor returned NULL'):
            with self.expect_signal():
                defs = Modulemd.ModuleStream.new(
                    Modulemd.ModuleStreamVersionEnum.LATEST + 1)

    def test_copy(self):
        for version in modulestream_versions:

            # Test that copying a stream with a stream name works
            stream = Modulemd.ModuleStream.new(version, 'foo', 'stable')
            copied_stream = stream.copy()

            assert copied_stream.props.module_name == stream.props.module_name
            assert copied_stream.get_module_name() == stream.get_module_name()
            assert copied_stream.props.stream_name == stream.props.stream_name
            assert copied_stream.get_stream_name() == stream.get_stream_name()

            # Test that copying a stream without a stream name works
            stream = Modulemd.ModuleStream.new(version, 'foo')
            copied_stream = stream.copy()

            assert copied_stream.props.module_name == stream.props.module_name
            assert copied_stream.get_module_name() == stream.get_module_name()
            assert copied_stream.props.stream_name == stream.props.stream_name
            assert copied_stream.get_stream_name() == stream.get_stream_name()

            # Test that copying a stream and changing the stream works
            stream = Modulemd.ModuleStream.new(version, 'foo', 'stable')
            copied_stream = stream.copy(module_stream='latest')

            assert copied_stream.props.module_name == stream.props.module_name
            assert copied_stream.get_module_name() == stream.get_module_name()
            assert copied_stream.props.stream_name != stream.props.stream_name
            assert copied_stream.get_stream_name() != stream.get_stream_name()
            assert copied_stream.props.stream_name == 'latest'
            assert copied_stream.get_stream_name() == 'latest'

            # Test that copying a stream without a module name works
            stream = Modulemd.ModuleStream.new(version, None, 'stable')
            copied_stream = stream.copy()

            assert copied_stream.props.module_name == stream.props.module_name
            assert copied_stream.get_module_name() == stream.get_module_name()
            assert copied_stream.props.stream_name == stream.props.stream_name
            assert copied_stream.get_stream_name() == stream.get_stream_name()

            # Test that copying a stream and changing the name works
            stream = Modulemd.ModuleStream.new(version, 'foo', 'stable')
            copied_stream = stream.copy(module_name='bar')

            assert copied_stream.props.module_name == 'bar'
            assert copied_stream.get_module_name() == 'bar'
            assert copied_stream.props.stream_name == stream.props.stream_name
            assert copied_stream.get_stream_name() == stream.get_stream_name()

            # Test the version and context
            assert copied_stream.props.version == 0
            assert copied_stream.get_version() == 0
            assert copied_stream.props.context is None
            assert copied_stream.get_context() is None

            # Set a version and check the copy
            stream.props.version = 42
            copied_stream = stream.copy()
            assert copied_stream.props.version == 42
            assert copied_stream.get_version() == 42

            # Set a context and check the copy
            stream.props.context = "c0ffee42"
            copied_stream = stream.copy()
            assert copied_stream.props.context == "c0ffee42"
            assert copied_stream.get_context() == "c0ffee42"

    def test_nsvc(self):
        for version in modulestream_versions:
            # First test that NSVC is None for a module with no name
            stream = Modulemd.ModuleStream.new(version)
            assert stream.get_nsvc() is None

            # Next, test for no stream name
            stream = Modulemd.ModuleStream.new(version, 'modulename')
            assert stream.get_nsvc() is None

            # Now with valid module and stream names
            stream = Modulemd.ModuleStream.new(
                version, 'modulename', 'streamname')
            assert stream.get_nsvc() == 'modulename:streamname:0'

            # Add a version number
            stream.props.version = 42
            assert stream.get_nsvc() == 'modulename:streamname:42'

            # Add a context
            stream.props.context = 'deadbeef'
            assert stream.get_nsvc() == 'modulename:streamname:42:deadbeef'

    def test_arch(self):
        for version in modulestream_versions:
            stream = Modulemd.ModuleStream.new(version)

            # Check the defaults
            assert stream.props.arch is None
            assert stream.get_arch() is None

            # Test property setting
            stream.props.arch = 'x86_64'
            assert stream.props.arch == 'x86_64'
            assert stream.get_arch() == 'x86_64'

            # Test set_arch()
            stream.set_arch('ppc64le')
            assert stream.props.arch == 'ppc64le'
            assert stream.get_arch() == 'ppc64le'

            # Test setting it to None
            stream.props.arch = None
            assert stream.props.arch is None
            assert stream.get_arch() is None

    def test_buildopts(self):
        for version in modulestream_versions:
            stream = Modulemd.ModuleStream.new(version)

            # Check the defaults
            assert stream.props.buildopts is None
            assert stream.get_buildopts() is None

            buildopts = Modulemd.Buildopts()
            buildopts.props.rpm_macros = '%demomacro 1'
            stream.set_buildopts(buildopts)

            assert stream.props.buildopts is not None
            assert stream.props.buildopts is not None
            assert stream.props.buildopts.props.rpm_macros == '%demomacro 1'

    def test_community(self):
        for version in modulestream_versions:
            stream = Modulemd.ModuleStream.new(version)

            # Check the defaults
            assert stream.props.community is None
            assert stream.get_community() is None

            # Test property setting
            stream.props.community = 'http://example.com'
            assert stream.props.community == 'http://example.com'
            assert stream.get_community() == 'http://example.com'

            # Test set_community()
            stream.set_community('http://redhat.com')
            assert stream.props.community == 'http://redhat.com'
            assert stream.get_community() == 'http://redhat.com'

            # Test setting it to None
            stream.props.community = None
            assert stream.props.community is None
            assert stream.get_community() is None

    def test_description(self):
        for version in modulestream_versions:
            stream = Modulemd.ModuleStream.new(version)

            # Check the defaults
            assert stream.get_description(locale="C") is None

            # Test set_description()
            stream.set_description('A different description')
            assert stream.get_description(
                locale="C") == 'A different description'

            # Test setting it to None
            stream.set_description(None)
            assert stream.get_description(locale="C") is None

    def test_documentation(self):
        for version in modulestream_versions:
            stream = Modulemd.ModuleStream.new(version)

            # Check the defaults
            assert stream.props.documentation is None
            assert stream.get_documentation() is None

            # Test property setting
            stream.props.documentation = 'http://example.com'
            assert stream.props.documentation == 'http://example.com'
            assert stream.get_documentation() == 'http://example.com'

            # Test set_documentation()
            stream.set_documentation('http://redhat.com')
            assert stream.props.documentation == 'http://redhat.com'
            assert stream.get_documentation() == 'http://redhat.com'

            # Test setting it to None
            stream.props.documentation = None
            assert stream.props.documentation is None
            assert stream.get_documentation() is None

    def test_summary(self):
        for version in modulestream_versions:
            stream = Modulemd.ModuleStream.new(version)

            # Check the defaults
            assert stream.get_summary(locale="C") is None

            # Test set_summary()
            stream.set_summary('A different summary')
            assert stream.get_summary(locale="C") == 'A different summary'

            # Test setting it to None
            stream.set_summary(None)
            assert stream.get_summary(locale="C") is None

    def test_tracker(self):
        for version in modulestream_versions:
            stream = Modulemd.ModuleStream.new(version)

            # Check the defaults
            assert stream.props.tracker is None
            assert stream.get_tracker() is None

            # Test property setting
            stream.props.tracker = 'http://example.com'
            assert stream.props.tracker == 'http://example.com'
            assert stream.get_tracker() == 'http://example.com'

            # Test set_tracker()
            stream.set_tracker('http://redhat.com')
            assert stream.props.tracker == 'http://redhat.com'
            assert stream.get_tracker() == 'http://redhat.com'

            # Test setting it to None
            stream.props.tracker = None
            assert stream.props.tracker is None
            assert stream.get_tracker() is None

    def test_components(self):
        for version in modulestream_versions:
            stream = Modulemd.ModuleStream.new(version)

            # Add an RPM component to a stream
            rpm_comp = Modulemd.ComponentRpm(name='rpmcomponent')
            stream.add_component(rpm_comp)
            assert 'rpmcomponent' in stream.get_rpm_component_names()
            retrieved_comp = stream.get_rpm_component('rpmcomponent')
            assert retrieved_comp
            assert retrieved_comp.props.name == 'rpmcomponent'

            # Add a Module component to a stream
            mod_comp = Modulemd.ComponentModule(name='modulecomponent')
            stream.add_component(mod_comp)
            assert 'modulecomponent' in stream.get_module_component_names()
            retrieved_comp = stream.get_module_component('modulecomponent')
            assert retrieved_comp
            assert retrieved_comp.props.name == 'modulecomponent'

            # Remove an RPM component from a stream
            stream.remove_rpm_component('rpmcomponent')

            # Remove a Module component from a stream
            stream.remove_module_component('modulecomponent')

    def test_licenses(self):
        for version in modulestream_versions:
            stream = Modulemd.ModuleStream.new(version)

            stream.add_content_license('GPLv2+')
            assert 'GPLv2+' in stream.get_content_licenses()

            stream.add_module_license('MIT')
            assert 'MIT' in stream.get_module_licenses()

            stream.remove_content_license('GPLv2+')
            stream.remove_module_license('MIT')

    def test_profiles(self):
        for version in modulestream_versions:
            stream = Modulemd.ModuleStream.new(version, 'sssd')

            profile = Modulemd.Profile(name='client')
            profile.add_rpm('sssd-client')

            stream.add_profile(profile)
            assert len(stream.get_profile_names()) == 1
            assert 'client' in stream.get_profile_names()
            assert 'sssd-client' in stream.get_profile(
                'client').get_rpms()

            stream.clear_profiles()
            assert len(stream.get_profile_names()) == 0

    def test_rpm_api(self):
        for version in modulestream_versions:
            stream = Modulemd.ModuleStream.new(version, 'sssd')

            stream.add_rpm_api('sssd-common')
            assert 'sssd-common' in stream.get_rpm_api()

            stream.remove_rpm_api('sssd-common')
            assert len(stream.get_rpm_api()) == 0

    def test_rpm_artifacts(self):
        for version in modulestream_versions:
            stream = Modulemd.ModuleStream.new(version)

            stream.add_rpm_artifact('bar-0:1.23-1.module_deadbeef.x86_64')
            assert 'bar-0:1.23-1.module_deadbeef.x86_64' in stream.get_rpm_artifacts()

            stream.remove_rpm_artifact('bar-0:1.23-1.module_deadbeef.x86_64')
            assert len(stream.get_rpm_artifacts()) == 0

    def test_rpm_filters(self):
        for version in modulestream_versions:
            stream = Modulemd.ModuleStream.new(version)

            stream.add_rpm_filter('bar')
            assert 'bar' in stream.get_rpm_filters()

            stream.remove_rpm_filter('bar')
            assert len(stream.get_rpm_filters()) == 0

    def test_servicelevels(self):
        for version in modulestream_versions:
            stream = Modulemd.ModuleStream.new(version)
            sl = Modulemd.ServiceLevel.new('rawhide')
            sl.set_eol_ymd(1980, 3, 2)

            stream.add_servicelevel(sl)

            assert 'rawhide' in stream.get_servicelevel_names()

            retrieved_sl = stream.get_servicelevel('rawhide')
            assert retrieved_sl.props.name == 'rawhide'
            assert retrieved_sl.get_eol_as_string() == '1980-03-02'

    def test_v1_eol(self):
        stream = Modulemd.ModuleStreamV1.new()
        eol = GLib.Date.new_dmy(3, 2, 1998)

        stream.set_eol(eol)
        retrieved_eol = stream.get_eol()

        assert retrieved_eol.get_day() == 3
        assert retrieved_eol.get_month() == 2
        assert retrieved_eol.get_year() == 1998

        sl = stream.get_servicelevel('rawhide')
        assert sl.get_eol_as_string() == '1998-02-03'

    def test_v1_dependencies(self):
        stream = Modulemd.ModuleStreamV1.new()
        stream.add_buildtime_requirement('testmodule', 'stable')

        assert len(stream.get_buildtime_modules()) == 1
        assert 'testmodule' in stream.get_buildtime_modules()

        assert stream.get_buildtime_requirement_stream('testmodule') == \
            'stable'

        stream.add_runtime_requirement('testmodule', 'latest')
        assert len(stream.get_runtime_modules()) == 1
        assert 'testmodule' in stream.get_runtime_modules()
        assert stream.get_runtime_requirement_stream('testmodule') == 'latest'

    def test_v2_dependencies(self):
        stream = Modulemd.ModuleStreamV2.new()
        deps = Modulemd.Dependencies()

        deps.add_buildtime_stream('foo', 'stable')
        deps.set_empty_runtime_dependencies_for_module('bar')
        stream.add_dependencies(deps)

        assert len(stream.get_dependencies()) == 1
        assert len(stream.get_dependencies()) == 1

        assert 'foo' in stream.get_dependencies(
        )[0].get_buildtime_modules()

        assert 'stable' in stream.get_dependencies(
        )[0].get_buildtime_streams('foo')

        assert 'bar' in stream.get_dependencies(
        )[0].get_runtime_modules()

    def test_xmd(self):
        if '_overrides_module' in dir(Modulemd):
            # The XMD python tests can only be run against the installed lib
            # because the overrides that translate between python and GVariant
            # must be installed in /usr/lib/python*/site-packages/gi/overrides
            # or they are not included when importing Modulemd
            stream = Modulemd.ModuleStreamV2.new()

            xmd = {'outer_key': ['scalar', {'inner_key': 'another_scalar'}]}

            stream.set_xmd(xmd)

            xmd_copy = stream.get_xmd()
            assert xmd_copy
            assert 'outer_key' in xmd
            assert 'scalar' in xmd['outer_key']
            assert 'inner_key' in xmd['outer_key'][1]
            assert xmd['outer_key'][1]['inner_key'] == 'another_scalar'

    def test_upgrade(self):
        v1_stream = Modulemd.ModuleStreamV1.new("SuperModule", "latest")
        v1_stream.set_summary("Summary")
        v1_stream.set_description("Description")
        v1_stream.add_module_license("BSD")

        v1_stream.add_buildtime_requirement("ModuleA", "streamZ")
        v1_stream.add_buildtime_requirement("ModuleB", "streamY")
        v1_stream.add_runtime_requirement("ModuleA", "streamZ")
        v1_stream.add_runtime_requirement("ModuleB", "streamY")

        v2_stream = v1_stream.upgrade(Modulemd.ModuleStreamVersionEnum.LATEST)
        self.assertIsNotNone(v2_stream)

        idx = Modulemd.ModuleIndex.new()
        idx.add_module_stream(v2_stream)

        self.assertEquals(idx.dump_to_string(), """---
document: modulemd
version: 2
data:
  name: SuperModule
  stream: latest
  summary: Summary
  description: Description
  license:
    module:
    - BSD
  dependencies:
  - buildrequires:
      ModuleA: [streamZ]
      ModuleB: [streamY]
    requires:
      ModuleA: [streamZ]
      ModuleB: [streamY]
...
""")

    def test_v2_yaml(self):
        yaml = """
---
document: modulemd
version: 2
data:
  name: modulename
  stream: streamname
  version: 1
  context: c0ffe3
  arch: x86_64
  summary: Module Summary
  description: Module Description
  api:
    rpms:
      - rpm_a
      - rpm_b
  filter:
    rpms: rpm_c

  artifacts:
    rpms:
      - bar-0:1.23-1.module_deadbeef.x86_64

  servicelevels:
    rawhide: {}
    production:
      eol: 2099-12-31

  license:
    content:
      - BSD
      - GPLv2+
    module: MIT

  dependencies:
    - buildrequires:
          platform: [-f27, -f28, -epel7]
      requires:
          platform: [-f27, -f28, -epel7]
    - buildrequires:
          platform: [f27]
          buildtools: [v1, v2]
          compatible: [v3]
      requires:
          platform: [f27]
          compatible: [v3, v4]
    - buildrequires:
          platform: [f28]
      requires:
          platform: [f28]
          runtime: [a, b]
    - buildrequires:
          platform: [epel7]
          extras: []
          moreextras: [foo, bar]
      requires:
          platform: [epel7]
          extras: []
          moreextras: [foo, bar]
  references:
        community: http://www.example.com/
        documentation: http://www.example.com/
        tracker: http://www.example.com/
  profiles:
        default:
            rpms:
                - bar
                - bar-extras
                - baz
        container:
            rpms:
                - bar
                - bar-devel
        minimal:
            description: Minimal profile installing only the bar package.
            rpms:
                - bar
        buildroot:
            rpms:
                - bar-devel
        srpm-buildroot:
            rpms:
                - bar-extras
  buildopts:
        rpms:
            macros: |
                %demomacro 1
                %demomacro2 %{demomacro}23
            whitelist:
                - fooscl-1-bar
                - fooscl-1-baz
                - xxx
                - xyz
  components:
        rpms:
            bar:
                rationale: We need this to demonstrate stuff.
                repository: https://pagure.io/bar.git
                cache: https://example.com/cache
                ref: 26ca0c0
            baz:
                rationale: This one is here to demonstrate other stuff.
            xxx:
                rationale: xxx demonstrates arches and multilib.
                arches: [i686, x86_64]
                multilib: [x86_64]
            xyz:
                rationale: xyz is a bundled dependency of xxx.
                buildorder: 10
        modules:
            includedmodule:
                rationale: Included in the stack, just because.
                repository: https://pagure.io/includedmodule.git
                ref: somecoolbranchname
                buildorder: 100
  xmd:
        some_key: some_data
        some_list:
            - a
            - b
        some_dict:
            a: alpha
            b: beta
            some_other_list:
                - c
                - d
            some_other_dict:
                another_key: more_data
                yet_another_key:
                    - this
                    - is
                    - getting
                    - silly
        can_bool: TRUE
...
"""
        stream = Modulemd.ModuleStream.read_string(yaml)

        assert stream is not None
        assert stream.props.module_name == 'modulename'
        assert stream.props.stream_name == 'streamname'
        assert stream.props.version == 1
        assert stream.props.context == 'c0ffe3'
        assert stream.props.arch == 'x86_64'
        assert stream.get_summary(locale="C") == "Module Summary"
        assert stream.get_description(
            locale="C") == "Module Description"

        assert 'rpm_a' in stream.get_rpm_api()
        assert 'rpm_b' in stream.get_rpm_api()

        assert 'rpm_c' in stream.get_rpm_filters()

        assert 'bar-0:1.23-1.module_deadbeef.x86_64' in stream.get_rpm_artifacts()

        assert 'rawhide' in stream.get_servicelevel_names()
        assert 'production' in stream.get_servicelevel_names()

        sl = stream.get_servicelevel('rawhide')
        assert sl is not None
        assert sl.props.name == 'rawhide'
        assert sl.get_eol() is None

        sl = stream.get_servicelevel('production')
        assert sl is not None
        assert sl.props.name == 'production'
        assert sl.get_eol() is not None
        assert sl.get_eol_as_string() == '2099-12-31'

        assert 'BSD' in stream.get_content_licenses()
        assert 'GPLv2+' in stream.get_content_licenses()
        assert 'MIT' in stream.get_module_licenses()

        assert len(stream.get_dependencies()) == 4

        assert stream.props.community == 'http://www.example.com/'
        assert stream.props.documentation == 'http://www.example.com/'
        assert stream.props.tracker == 'http://www.example.com/'

        assert len(stream.get_profile_names()) == 5

        buildopts = stream.get_buildopts()
        assert buildopts is not None

        assert '%demomacro 1\n%demomacro2 %{demomacro}23\n' == buildopts.props.rpm_macros
        assert 'fooscl-1-bar' in buildopts.get_rpm_whitelist()
        assert 'fooscl-1-baz' in buildopts.get_rpm_whitelist()
        assert 'xxx' in buildopts.get_rpm_whitelist()
        assert 'xyz' in buildopts.get_rpm_whitelist()

        if os.getenv('MMD_TEST_INSTALLED_LIB'):
            # The XMD python tests can only be run against the installed
            # lib because the overrides that translate between python and
            # GVariant must be installed in
            # /usr/lib/python*/site-packages/gi/overrides
            # or they are not included when importing Modulemd
            xmd = stream.get_xmd()
            assert xmd is not None

            assert 'some_key' in xmd
            assert xmd['some_key'] == 'some_data'

            assert 'some_list' in xmd

            assert 'a' in xmd['some_list']
            assert 'b' in xmd['some_list']

            assert 'some_dict' in xmd
            assert 'a' in xmd['some_dict']
            assert xmd['some_dict']['a'] == 'alpha'

            assert 'some_other_dict' in xmd['some_dict']
            assert 'yet_another_key' in xmd[
                'some_dict']['some_other_dict']
            assert 'silly' in xmd['some_dict'][
                'some_other_dict']['yet_another_key']

            assert 'can_bool' in xmd
            assert xmd['can_bool'] is True

        # Validate a trivial modulemd
        trivial_yaml = """
---
document: modulemd
version: 2
data:
    summary: Trivial Summary
    description: Trivial Description
    license:
        module: MIT
...
"""

        stream = Modulemd.ModuleStream.read_string(trivial_yaml)
        assert stream

        # Sanity check of spec.v2.yaml
        stream = Modulemd.ModuleStream.read_file(
            "%s/spec.v2.yaml" % os.getenv('MESON_SOURCE_ROOT'))
        assert stream

    def test_v1_yaml(self):
        for version in modulestream_versions:
            yaml = """
---
document: modulemd
version: 1
data:
  name: modulename
  stream: streamname
  version: 1
  context: c0ffe3
  arch: x86_64
  summary: Module Summary
  description: Module Description
  api:
    rpms:
      - rpm_a
      - rpm_b
  filter:
    rpms: rpm_c

  artifacts:
    rpms:
      - bar-0:1.23-1.module_deadbeef.x86_64

  eol: 2033-08-04
  servicelevels:
    foo: {}
    production:
      eol: 2099-12-31

  license:
    content:
      - BSD
      - GPLv2+
    module: MIT

  dependencies:
        buildrequires:
            platform: and-its-stream-name
            extra-build-env: and-its-stream-name-too
        requires:
            runtimeplatform: and-its-stream-name-2

  references:
        community: http://www.example.com/
        documentation: http://www.example.com/
        tracker: http://www.example.com/
  profiles:
        default:
            rpms:
                - bar
                - bar-extras
                - baz
        container:
            rpms:
                - bar
                - bar-devel
        minimal:
            description: Minimal profile installing only the bar package.
            rpms:
                - bar
        buildroot:
            rpms:
                - bar-devel
        srpm-buildroot:
            rpms:
                - bar-extras
  buildopts:
        rpms:
            macros: |
                %demomacro 1
                %demomacro2 %{demomacro}23
            whitelist:
                - fooscl-1-bar
                - fooscl-1-baz
                - xxx
                - xyz
  components:
        rpms:
            bar:
                rationale: We need this to demonstrate stuff.
                repository: https://pagure.io/bar.git
                cache: https://example.com/cache
                ref: 26ca0c0
            baz:
                rationale: This one is here to demonstrate other stuff.
            xxx:
                rationale: xxx demonstrates arches and multilib.
                arches: [i686, x86_64]
                multilib: [x86_64]
            xyz:
                rationale: xyz is a bundled dependency of xxx.
                buildorder: 10
        modules:
            includedmodule:
                rationale: Included in the stack, just because.
                repository: https://pagure.io/includedmodule.git
                ref: somecoolbranchname
                buildorder: 100
  xmd:
        some_key: some_data
        some_list:
            - a
            - b
        some_dict:
            a: alpha
            b: beta
            some_other_list:
                - c
                - d
            some_other_dict:
                another_key: more_data
                yet_another_key:
                    - this
                    - is
                    - getting
                    - silly
        can_bool: TRUE
...
"""
            stream = Modulemd.ModuleStream.read_string(yaml)

            assert stream is not None
            assert stream.props.module_name == 'modulename'
            assert stream.props.stream_name == 'streamname'
            assert stream.props.version == 1
            assert stream.props.context == 'c0ffe3'
            assert stream.props.arch == 'x86_64'
            assert stream.get_summary(locale="C") == "Module Summary"
            assert stream.get_description(
                locale="C") == "Module Description"

            assert 'rpm_a' in stream.get_rpm_api()
            assert 'rpm_b' in stream.get_rpm_api()

            assert 'rpm_c' in stream.get_rpm_filters()

            assert 'bar-0:1.23-1.module_deadbeef.x86_64' in stream.get_rpm_artifacts()

            assert 'rawhide' in stream.get_servicelevel_names()
            assert 'production' in stream.get_servicelevel_names()

            sl = stream.get_servicelevel('rawhide')
            assert sl is not None
            assert sl.props.name == 'rawhide'
            assert sl.get_eol_as_string() == '2033-08-04'

            sl = stream.get_servicelevel('foo')
            assert sl is not None
            assert sl.props.name == 'foo'
            assert sl.get_eol() is None

            sl = stream.get_servicelevel('production')
            assert sl is not None
            assert sl.props.name == 'production'
            assert sl.get_eol() is not None
            assert sl.get_eol_as_string() == '2099-12-31'

            assert 'BSD' in stream.get_content_licenses()
            assert 'GPLv2+' in stream.get_content_licenses()
            assert 'MIT' in stream.get_module_licenses()

            buildrequires = stream.get_buildtime_modules()
            assert len(buildrequires) == 2
            assert 'platform' in buildrequires
            assert stream.get_buildtime_requirement_stream(
                'platform') == 'and-its-stream-name'
            assert 'extra-build-env' in buildrequires
            assert stream.get_buildtime_requirement_stream(
                'extra-build-env') == 'and-its-stream-name-too'

            requires = stream.get_runtime_modules()
            assert len(requires) == 1
            assert 'runtimeplatform' in requires
            assert stream.get_runtime_requirement_stream(
                'runtimeplatform') == 'and-its-stream-name-2'

            assert stream.props.community == 'http://www.example.com/'
            assert stream.props.documentation == 'http://www.example.com/'
            assert stream.props.tracker == 'http://www.example.com/'

            assert len(stream.get_profile_names()) == 5

            buildopts = stream.get_buildopts()
            assert buildopts is not None

            assert '%demomacro 1\n%demomacro2 %{demomacro}23\n' == buildopts.props.rpm_macros
            assert 'fooscl-1-bar' in buildopts.get_rpm_whitelist()
            assert 'fooscl-1-baz' in buildopts.get_rpm_whitelist()
            assert 'xxx' in buildopts.get_rpm_whitelist()
            assert 'xyz' in buildopts.get_rpm_whitelist()

            if os.getenv('MMD_TEST_INSTALLED_LIB'):
                # The XMD python tests can only be run against the installed
                # lib because the overrides that translate between python and
                # GVariant must be installed in
                # /usr/lib/python*/site-packages/gi/overrides
                # or they are not included when importing Modulemd
                xmd = stream.get_xmd()
                assert xmd is not None

                assert 'some_key' in xmd
                assert xmd['some_key'] == 'some_data'

                assert 'some_list' in xmd

                assert 'a' in xmd['some_list']
                assert 'b' in xmd['some_list']

                assert 'some_dict' in xmd
                assert 'a' in xmd['some_dict']
                assert xmd['some_dict']['a'] == 'alpha'

                assert 'some_other_dict' in xmd['some_dict']
                assert 'yet_another_key' in xmd[
                    'some_dict']['some_other_dict']
                assert 'silly' in xmd['some_dict'][
                    'some_other_dict']['yet_another_key']

                assert 'can_bool' in xmd
                assert xmd['can_bool'] is True

            # Validate a trivial modulemd
            trivial_yaml = """
---
document: modulemd
version: 1
data:
  summary: Trivial Summary
  description: Trivial Description
  license:
    module: MIT
...
"""

            stream = Modulemd.ModuleStream.read_string(trivial_yaml)
            assert stream

            # Sanity check of spec.v1.yaml
            stream = Modulemd.ModuleStream.read_file(
                "%s/spec.v1.yaml" % os.getenv('MESON_SOURCE_ROOT'))
            assert stream


if __name__ == '__main__':
    unittest.main()