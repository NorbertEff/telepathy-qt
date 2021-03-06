#!/usr/bin/python
#
# Copyright (C) 2012 Collabora Limited <http://www.collabora.co.uk>
# Copyright (C) 2012 Nokia Corporation
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from sys import argv
import xml.dom.minidom
import codecs
from getopt import gnu_getopt

from libtpcodegen import NS_TP, get_descendant_text, get_by_path
from libqtcodegen import binding_from_usage, extract_arg_or_member_info, format_docstring, gather_externals, gather_custom_lists, get_headerfile_cmd, get_qt_name, qt_identifier_escape, RefRegistry

# TODO generate docstrings

def to_lower_camel_case(s):
    if len(s) <= 1:
        return s.lower()

    i = 0
    for c in s:
        if c == '_':
            break
        i += 1

    ret = s
    if i == len(s):
        return s.lower()
    else:
        ret = s[0:i].lower() + s[i:]
    ret = ret.replace('_', '')
    return ret

class Generator(object):
    def __init__(self, opts):
        try:
            self.group = opts.get('--group', '')
            self.headerfile = opts['--headerfile']
            self.implfile = opts['--implfile']
            self.namespace = opts['--namespace']
            self.typesnamespace = opts['--typesnamespace']
            self.realinclude = opts.get('--realinclude', None)
            self.mocinclude = opts.get('--mocinclude', None)
            self.prettyinclude = opts.get('--prettyinclude')
            self.extraincludes = opts.get('--extraincludes', None)
            self.must_define = opts.get('--must-define', None)
            self.visibility = opts.get('--visibility', '')
            ifacedom = xml.dom.minidom.parse(opts['--ifacexml'])
            specdom = xml.dom.minidom.parse(opts['--specxml'])
        except KeyError, k:
            assert False, 'Missing required parameter %s' % k.args[0]

        if not self.realinclude:
            self.realinclude = self.headerfile

        self.hs = []
        self.bs = []
        self.ifacenodes = ifacedom.getElementsByTagName('node')
        self.spec, = get_by_path(specdom, "spec")
        self.custom_lists = gather_custom_lists(self.spec, self.typesnamespace)
        self.externals = gather_externals(self.spec)
        self.refs = RefRegistry(self.spec)

    def __call__(self):
        # Output info header and includes
        self.h("""\
/*
 * This file contains D-Bus adaptor classes generated by qt-svc-gen.py.
 *
 * This file can be distributed under the same terms as the specification from
 * which it was generated.
 */
""")

        if self.must_define:
            self.h('\n')
            self.h('#ifndef %s\n' % self.must_define)
            self.h('#error %s\n' % self.must_define)
            self.h('#endif\n')

        self.h('\n')

        if self.extraincludes:
            for include in self.extraincludes.split(','):
                self.h('#include %s\n' % include)

        self.h("""\
#include <TelepathyQt/AbstractAdaptor>
#include <TelepathyQt/Global>
#include <TelepathyQt/Types>

#include <QObject>
#include <QtDBus>

""")

        if self.must_define:
            self.b("""#define %s\n""" % (self.must_define))

        self.b("""#include "%s"

""" % self.realinclude)

        if self.mocinclude:
            self.b("""#include "%s"

""" % self.mocinclude)

            self.b("""\
#include <TelepathyQt/Constants>
#include <TelepathyQt/MethodInvocationContext>

""")

        # Begin namespace
        for ns in self.namespace.split('::'):
            self.hb("""\
namespace %s
{
""" % ns)

        # Output interface proxies
        def ifacenodecmp(x, y):
            xname, yname = [self.namespace + '::' + node.getAttribute('name').replace('/', '').replace('_', '') + 'Adaptor' for node in x, y]

            return cmp(xname, yname)

        self.ifacenodes.sort(cmp=ifacenodecmp)
        for ifacenode in self.ifacenodes:
            self.do_ifacenode(ifacenode)

        # End namespace
        self.hb(''.join(['\n}' for ns in self.namespace.split('::')]))

        # Write output to files
        (codecs.getwriter('utf-8')(open(self.headerfile, 'w'))).write(''.join(self.hs))
        (codecs.getwriter('utf-8')(open(self.implfile, 'w'))).write(''.join(self.bs))

    def do_ifacenode(self, ifacenode):
        # Extract info
        name = ifacenode.getAttribute('name').replace('/', '').replace('_', '') + 'Adaptor'
        iface, = get_by_path(ifacenode, 'interface')
        dbusname = iface.getAttribute('name')
        props = get_by_path(iface, 'property')
        methods = get_by_path(iface, 'method')
        signals = get_by_path(iface, 'signal')

        # Begin class, constructors
        self.h("""
/**
 * \\class %(name)s
%(headercmd)s\
%(groupcmd)s\
 *
 * Adaptor class providing a 1:1 mapping of the D-Bus interface "%(dbusname)s".
 */
class %(visibility)s %(name)s : public Tp::AbstractAdaptor
{
    Q_OBJECT
    Q_CLASSINFO("D-Bus Interface", "%(dbusname)s")
    Q_CLASSINFO("D-Bus Introspection", ""
"  <interface name=\\"%(dbusname)s\\">\\n"
""" % {'name': name,
       'headercmd': get_headerfile_cmd(self.realinclude, self.prettyinclude),
       'groupcmd': self.group and (' * \\ingroup %s\n' % self.group),
       'dbusname': dbusname,
       'visibility': self.visibility,
       })

        self.do_introspection(props, methods, signals)

        self.h("""\
"  </interface>\\n"
"")
""")

        self.do_qprops(props)

        self.h("""
public:
    %(name)s(const QDBusConnection& dbusConnection, QObject* adaptee, QObject* parent);
    virtual ~%(name)s();

""" % {'name': name})

        self.do_mic_typedefs(methods)

        self.b("""
%(name)s::%(name)s(const QDBusConnection& bus, QObject* adaptee, QObject* parent)
    : Tp::AbstractAdaptor(bus, adaptee, parent)
{
""" % {'name': name})

        self.do_signals_connect(signals)

        self.b("""\
}

%(name)s::~%(name)s()
{
}
""" % {'name': name})

        # Properties
        has_props = False
        if props:
            self.h("""
public: // PROPERTIES
""")

            for prop in props:
                # Skip tp:properties
                if not prop.namespaceURI:
                    self.do_prop(name, prop)
                    has_props = True

        # Methods
        if methods:
            self.h("""
public Q_SLOTS: // METHODS
""")

            for method in methods:
                self.do_method(name, method)

        # Signals
        if signals:
            self.h("""
Q_SIGNALS: // SIGNALS
""")

            for signal in signals:
                self.do_signal(signal)

        # Close class
        self.h("""\
};
""")

    def do_introspection(self, props, methods, signals):
        self.do_prop_introspection(props)
        self.do_method_introspection(methods)
        self.do_signal_introspection(signals)

    def do_prop_introspection(self, props):
        for prop in props:
            if prop.namespaceURI:
                continue

            name = prop.getAttribute('name')
            access = prop.getAttribute('access')
            sig = prop.getAttribute('type')
            tptype = prop.getAttributeNS(NS_TP, 'type')
            binding = binding_from_usage(sig, tptype, self.custom_lists, (sig, tptype) in self.externals, self.typesnamespace)

            if not binding.custom_type:
                self.h("""\
"    <property access=\\"%(access)s\\" type=\\"%(sig)s\\" name=\\"%(name)s\\"/>\\n"
""" % {'access': access,
       'sig': sig,
       'name': name,
       })
            else:
                self.h("""\
"    <property access=\\"%(access)s\\" type=\\"%(sig)s\\" name=\\"%(name)s\\">\\n"
"      <annotation value=\\"%(type)s\\" name=\\"com.trolltech.QtDBus.QtTypeName\\"/>\\n"
"    </property>\\n"
""" % {'access': access,
       'sig': sig,
       'name': name,
       'type': binding.val,
       })

    def do_method_introspection(self, methods):
        for method in methods:
            name = method.getAttribute('name')
            args = get_by_path(method, 'arg')
            argnames, argdocstrings, argbindings = extract_arg_or_member_info(args,
                self.custom_lists, self.externals, self.typesnamespace, self.refs, '     *     ')

            if not argnames:
                self.h("""\
"    <method name=\\"%(name)s\\"/>\\n"
""" % {'name': name})
            else:
                self.h("""\
"    <method name=\\"%(name)s\\">\\n"
""" % {'name': name})

                outindex = 0
                inindex = 0
                for i in xrange(len(argnames)):
                    assert argnames[i] != None, 'Name missing from argument at index %d for signal %s' % (i, name)

                    argbinding = argbindings[i]
                    argname = argnames[i]
                    argsig = args[i].getAttribute('type')
                    argdirection = args[i].getAttribute('direction')

                    # QtDBus requires annotating a{sv}
                    if argsig == 'a{sv}':
                        argbinding.custom_type = True

                    if not argbinding.custom_type:
                        self.h("""\
"      <arg direction=\\"%(direction)s\\" type=\\"%(sig)s\\" name=\\"%(name)s\\"/>\\n"
""" % {'direction': argdirection,
       'sig': argsig,
       'name': argname})
                    else:
                        self.h("""\
"      <arg direction=\\"%(direction)s\\" type=\\"%(sig)s\\" name=\\"%(name)s\\">\\n"
"        <annotation value=\\"%(type)s\\" name=\\"com.trolltech.QtDBus.QtTypeName.%(index)s\\"/>\\n"
"      </arg>\\n"
""" % {'direction': argdirection,
       'sig': argsig,
       'name': argname,
       'type': argbinding.val,
       'index': 'In' + str(inindex) if argdirection == 'in' else 'Out' + str(outindex),
       })

                    if argdirection == 'out':
                        outindex += 1
                    else:
                        inindex += 1

                self.h("""\
"    </method>\\n"
""")

    def do_signal_introspection(self, signals):
        for signal in signals:
            name = signal.getAttribute('name')
            args = get_by_path(signal, 'arg')
            argnames, argdocstrings, argbindings = extract_arg_or_member_info(args,
                self.custom_lists, self.externals, self.typesnamespace, self.refs, '     *     ')

            if not argnames:
                self.h("""\
"    <signal name=\\"%(name)s\\"/>\\n"
""" % {'name': name})
            else:
                self.h("""\
"    <signal name=\\"%(name)s\\">\\n"
""" % {'name': name})

                for i in xrange(len(argnames)):
                    assert argnames[i] != None, 'Name missing from argument at index %d for signal %s' % (i, name)

                    argbinding = argbindings[i]
                    argname = argnames[i]
                    argsig = args[i].getAttribute('type')

                    if not argbinding.custom_type:
                        self.h("""\
"      <arg type=\\"%(sig)s\\" name=\\"%(name)s\\"/>\\n"
""" % {'sig': argsig,
       'name': argname})
                    else:
                        self.h("""\
"      <arg type=\\"%(sig)s\\" name=\\"%(name)s\\">\\n"
"        <annotation value=\\"%(type)s\\" name=\\"com.trolltech.QtDBus.QtTypeName.In%(index)d\\"/>\\n"
"      </arg>\\n"
""" % {'sig': argsig,
       'name': argname,
       'type': argbinding.val,
       'index': i,
       })

                self.h("""\
"    </signal>\\n"
""")

    def do_mic_typedefs(self, methods):
        for method in methods:
            name = method.getAttribute('name')
            args = get_by_path(method, 'arg')
            argnames, argdocstrings, argbindings = extract_arg_or_member_info(args, self.custom_lists,
                    self.externals, self.typesnamespace, self.refs, '     *     ')

            outargs = []
            for i in xrange(len(args)):
                if args[i].getAttribute('direction') == 'out':
                    outargs.append(i)

            if outargs:
                outargtypes = ', '.join([argbindings[i].val for i in outargs])
            else:
                outargtypes = ''

            self.h("""\
    typedef Tp::MethodInvocationContextPtr< %(outargtypes)s > %(name)sContextPtr;
""" % {'name': name,
       'outargtypes': outargtypes,
       })

    def do_qprops(self, props):
        for prop in props:
            # Skip tp:properties
            if not prop.namespaceURI:
                self.do_qprop(prop)

    def do_qprop(self, prop):
        name = prop.getAttribute('name')
        access = prop.getAttribute('access')
        gettername = name
        settername = None
        if 'write' in access:
            settername = 'Set' + name

        sig = prop.getAttribute('type')
        tptype = prop.getAttributeNS(NS_TP, 'type')
        binding = binding_from_usage(sig, tptype, self.custom_lists, (sig, tptype) in self.externals, self.typesnamespace)

        self.h("""\
    Q_PROPERTY(%(type)s %(name)s %(getter)s %(setter)s)
""" % {'type': binding.val,
       'name': name,
       'getter': 'READ ' + gettername if ('read' in access) else '',
       'setter': 'WRITE ' + settername if ('write' in access) else '',
       })

    def do_prop(self, ifacename, prop):
        name = prop.getAttribute('name')
        adaptee_name = to_lower_camel_case(prop.getAttribute('tp:name-for-bindings'))
        access = prop.getAttribute('access')
        gettername = name
        settername = None
        if 'write' in access:
            settername = 'Set' + name
        docstring = format_docstring(prop, self.refs, '     * ').replace('*/', '&#42;&#47;')

        sig = prop.getAttribute('type')
        tptype = prop.getAttributeNS(NS_TP, 'type')
        binding = binding_from_usage(sig, tptype, self.custom_lists, (sig, tptype) in self.externals, self.typesnamespace)

        if 'read' in access:
            self.h("""\
    /**
     * Return the value of the exported D-Bus object property \\c %(name)s of type \\c %(type)s.
     *
     * Adaptees should export this property as a Qt property named
     * '%(adaptee_name)s' with type %(type)s.
     *
%(docstring)s\
     *
     * \\return The value of exported property \\c %(name)s.
     */
    %(type)s %(gettername)s() const;
""" % {'name': name,
       'adaptee_name': adaptee_name,
       'docstring': docstring,
       'type': binding.val,
       'gettername': gettername,
       })

            self.b("""
%(type)s %(ifacename)s::%(gettername)s() const
{
    return qvariant_cast< %(type)s >(adaptee()->property("%(adaptee_name)s"));
}
""" % {'type': binding.val,
       'ifacename': ifacename,
       'gettername': gettername,
       'adaptee_name': adaptee_name,
       })

        if 'write' in access:
            self.h("""\
    /**
     * Set the value of the exported D-Bus object property \\c %(name)s of type \\c %(type)s.
     *
     * Adaptees should export this property as a writable Qt property named
     * '%(adaptee_name)s' with type %(type)s.
     *
%(docstring)s\
     */
    void %(settername)s(const %(type)s &newValue);
""" % {'name': name,
       'adaptee_name': adaptee_name,
       'docstring': docstring,
       'settername': settername,
       'type': binding.val,
       })

            self.b("""
void %(ifacename)s::%(settername)s(const %(type)s &newValue)
{
    adaptee()->setProperty("%(adaptee_name)s", qVariantFromValue(newValue));
}
""" % {'ifacename': ifacename,
       'settername': settername,
       'type': binding.val,
       'adaptee_name': adaptee_name,
       })

    def do_method(self, ifacename, method):
        name = method.getAttribute('name')
        adaptee_name = to_lower_camel_case(method.getAttribute('tp:name-for-bindings'))
        args = get_by_path(method, 'arg')
        argnames, argdocstrings, argbindings = extract_arg_or_member_info(args, self.custom_lists,
                self.externals, self.typesnamespace, self.refs, '     *     ')
        docstring = format_docstring(method, self.refs, '     * ').replace('*/', '&#42;&#47;')

        inargs = []
        outargs = []

        for i in xrange(len(args)):
            if args[i].getAttribute('direction') == 'out':
                outargs.append(i)
            else:
                inargs.append(i)
                assert argnames[i] != None, 'No argument name for input argument at index %d for method %s' % (i, name)

        if outargs:
            rettype = argbindings[outargs[0]].val
        else:
            rettype = 'void'

        params = [argbindings[i].inarg + ' ' + argnames[i] for i in inargs]
        params.append('const QDBusMessage& dbusMessage')
        params += [argbindings[i].outarg + ' ' + argnames[i] for i in outargs[1:]]
        params = ', '.join(params)

        if outargs:
            outargtypes = ', '.join([argbindings[i].val for i in outargs])
        else:
            outargtypes = ''
        invokemethodargs = ', '.join(['Q_ARG(' + argbindings[i].val + ', ' + argnames[i] + ')' for i in inargs])

        inparams = [argbindings[i].val for i in inargs]
        inparams.append("%s::%s::%sContextPtr" % (self.namespace, ifacename, name))
        normalized_adaptee_params = ','.join(inparams)

        adaptee_params = [argbindings[i].inarg + ' ' + argnames[i] for i in inargs]
        adaptee_params.append('const %(namespace)s::%(ifacename)s::%(name)sContextPtr &context' %
            {'namespace': self.namespace,
             'ifacename': ifacename,
             'name': name})
        adaptee_params = ', '.join(adaptee_params)

        self.h("""\
    /**
     * Begins a call to the exported D-Bus method \\c %(name)s on this object.
     *
     * Adaptees should export this method as a Qt slot with the following signature:
     * void %(adaptee_name)s(%(adaptee_params)s);
     *
     * Implementations should call MethodInvocationContext::setFinished (or setFinishedWithError
     * accordingly) on the received \\a context object once the method has finished processing.
     *
%(docstring)s\
     *
""" % {'name': name,
        'adaptee_name': adaptee_name,
        'adaptee_params': adaptee_params,
        'rettype': rettype,
        'docstring': docstring
        })

        for i in inargs:
            if argdocstrings[i]:
                self.h("""\
     * \\param %s
%s\
""" % (argnames[i], argdocstrings[i]))

        for i in outargs[1:]:
            if argdocstrings[i]:
                self.h("""\
     * \\param %s Output parameter
%s\
""" % (argnames[i], argdocstrings[i]))

        if outargs:
                self.h("""\
     * \\return
%s\
""" % argdocstrings[outargs[0]])

        self.h("""\
     */
    %(rettype)s %(name)s(%(params)s);
""" % {'rettype': rettype,
       'name': name,
       'params': params
       })

        self.b("""
%(rettype)s %(ifacename)s::%(name)s(%(params)s)
{
    if (adaptee()->metaObject()->indexOfMethod("%(adaptee_name)s(%(normalized_adaptee_params)s)") < 0) {
        dbusConnection().send(dbusMessage.createErrorReply(TP_QT_ERROR_NOT_IMPLEMENTED, QLatin1String("Not implemented")));
""" % {'rettype': rettype,
       'ifacename': ifacename,
       'name': name,
       'adaptee_name': adaptee_name,
       'normalized_adaptee_params': normalized_adaptee_params,
       'params': params,
       })

        if rettype != 'void':
            self.b("""\
        return %(rettype)s();
""" % {'rettype': rettype})
        else:
            self.b("""\
        return;
""")

        self.b("""\
    }

    %(name)sContextPtr ctx = %(name)sContextPtr(
            new Tp::MethodInvocationContext< %(outargtypes)s >(dbusConnection(), dbusMessage));
""" % {'name': name,
       'outargtypes': outargtypes,
       })

        if invokemethodargs:
            self.b("""\
    QMetaObject::invokeMethod(adaptee(), "%(adaptee_name)s",
        %(invokemethodargs)s,
        Q_ARG(%(namespace)s::%(ifacename)s::%(name)sContextPtr, ctx));
""" % {'namespace': self.namespace,
       'ifacename': ifacename,
       'name': name,
       'adaptee_name': adaptee_name,
       'invokemethodargs': invokemethodargs,
       })
        else:
            self.b("""\
    QMetaObject::invokeMethod(adaptee(), "%(lname)s",
        Q_ARG(%(namespace)s::%(ifacename)s::%(name)sContextPtr, ctx));
""" % {'namespace': self.namespace,
       'ifacename': ifacename,
       'name': name,
       'lname': (name[0].lower() + name[1:]),
       })

        if rettype != 'void':
            self.b("""\
    return %(rettype)s();
""" % {'rettype': rettype})

        self.b("}\n")

    def do_signal(self, signal):
        name = signal.getAttribute('name')
        adaptee_name = to_lower_camel_case(signal.getAttribute('tp:name-for-bindings'))
        argnames, argdocstrings, argbindings = extract_arg_or_member_info(get_by_path(signal,
            'arg'), self.custom_lists, self.externals, self.typesnamespace, self.refs, '     *     ')
        params = ', '.join(['%s %s' % (binding.inarg, param_name) for binding, param_name in zip(argbindings, argnames)])

        for i in xrange(len(argnames)):
            assert argnames[i] != None, 'Name missing from argument at index %d for signal %s' % (i, name)

        self.h("""\
    /**
     * Represents the exported D-Bus signal \\c %(name)s on this object.
     *
     * Adaptees should export this signal as a Qt signal with the following signature:
     * void %(adaptee_name)s(%(params)s);
     *
     * The adaptee signal will be automatically relayed as a D-Bus signal once emitted.
     *
""" % {'name': name,
       'adaptee_name': adaptee_name,
       'params': params
       })

        for i in xrange(len(argnames)):
            assert argnames[i] != None, 'Name missing from argument at index %d for signal %s' % (i, name)
            if argdocstrings[i]:
                self.h("""\
     * \\param %s
%s\
""" % (argnames[i], argdocstrings[i]))

        self.h("""\
     */
    void %(name)s(%(params)s);
""" % {'name': name,
       'params': params
       })

    def do_signals_connect(self, signals):
        for signal in signals:
            name = signal.getAttribute('name')
            adaptee_name = to_lower_camel_case(signal.getAttribute('tp:name-for-bindings'))
            _, _, argbindings = extract_arg_or_member_info(get_by_path(signal, 'arg'),
                    self.custom_lists, self.externals, self.typesnamespace, self.refs, '     *     ')

            self.b("""\
    connect(adaptee, SIGNAL(%(adaptee_name)s(%(params)s)), SIGNAL(%(name)s(%(params)s)));
""" % {'name': name,
       'adaptee_name': adaptee_name,
       'params': ', '.join([binding.inarg for binding in argbindings])
       })

    def h(self, str):
        self.hs.append(str)

    def b(self, str):
        self.bs.append(str)

    def hb(self, str):
        self.h(str)
        self.b(str)


if __name__ == '__main__':
    options, argv = gnu_getopt(argv[1:], '',
            ['group=',
             'headerfile=',
             'implfile=',
             'namespace=',
             'typesnamespace=',
             'realinclude=',
             'mocinclude=',
             'prettyinclude=',
             'extraincludes=',
             'must-define=',
             'visibility=',
             'ifacexml=',
             'specxml='])

    Generator(dict(options))()
