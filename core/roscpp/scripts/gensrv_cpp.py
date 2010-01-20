#!/usr/bin/env python
# Software License Agreement (BSD License)
#
# Copyright (c) 2009, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

## ROS message source code generation for C++
## 
## Converts ROS .msg files in a package into C++ source code implementations.

import roslib; roslib.load_manifest('roscpp')
 
import sys
import os
import traceback

# roslib.msgs contains the utilities for parsing .msg specifications. It is meant to have no rospy-specific knowledge
import roslib.srvs
import roslib.packages
import roslib.gentools

import genmsg_cpp

from cStringIO import StringIO

def write_begin(s, pkg, srv, file):
    s.write("/* Auto-generated by genmsg_cpp for file %s */\n"%(file))
    s.write('#ifndef %s_SERVICE_%s_H\n'%(pkg.upper(), srv.upper()))
    s.write('#define %s_SERVICE_%s_H\n'%(pkg.upper(), srv.upper()))

def write_end(s, pkg, srv):
    s.write('#endif // %s_SERVICE_%s_H\n'%(pkg.upper(), srv.upper()))
    
def write_generic_includes(s):
    s.write('#include "ros/service_traits.h"\n\n')
    
def write_trait_char_class(s, class_name, cpp_msg, value):
    s.write('template<>\nstruct %s<%s> {\n'%(class_name, cpp_msg))
    s.write('  static const char* value() \n  {\n    return "%s";\n  }\n\n'%(value))
    s.write('  static const char* value(const %s&) { return value(); } \n'%(cpp_msg))
    s.write('};\n\n')
    
def write_traits(s, spec, pkg, msg, cpp_name_prefix):
    gendeps_dict = roslib.gentools.get_dependencies(spec, pkg)
    md5sum = roslib.gentools.compute_md5(gendeps_dict)
    datatype = '%s/%s'%(pkg, msg)
    
    cpp_msg = '%s%s'%(cpp_name_prefix, msg)
    s.write('namespace ros\n{\n')
    s.write('namespace service_traits\n{\n')
    
    write_trait_char_class(s, 'MD5Sum', cpp_msg, md5sum);
    write_trait_char_class(s, 'DataType', cpp_msg, datatype);
    request_with_allocator = '%s::Request_<Allocator> '%(cpp_msg)
    response_with_allocator = '%s::Response_<Allocator> '%(cpp_msg)
    genmsg_cpp.write_trait_char_class(s, 'MD5Sum', request_with_allocator, md5sum)
    genmsg_cpp.write_trait_char_class(s, 'DataType', request_with_allocator, datatype)
    genmsg_cpp.write_trait_char_class(s, 'MD5Sum', response_with_allocator, md5sum)
    genmsg_cpp.write_trait_char_class(s, 'DataType', response_with_allocator, datatype)
    s.write('} // namespace message_traits\n')
    s.write('} // namespace ros\n\n')

def generate(srv_path):
    (package_dir, package) = roslib.packages.get_dir_pkg(srv_path)
    (name, spec) = roslib.srvs.load_from_file(srv_path)
    
    s = StringIO()  
    cpp_prefix = '%s::%s::'%(package, name)
    write_begin(s, package, name, srv_path)
    genmsg_cpp.write_generic_includes(s)
    write_generic_includes(s)
    genmsg_cpp.write_includes(s, spec.request, package)
    s.write('\n')
    genmsg_cpp.write_includes(s, spec.response, package)
    
    s.write('namespace %s\n{\n'%(package))
    s.write('struct %s\n{\n'%(name))
    genmsg_cpp.write_struct(s, spec.request, package, "Request", cpp_prefix)
    s.write('\n')
    genmsg_cpp.write_struct(s, spec.response, package, "Response", cpp_prefix)
    s.write('\n')
    s.write('Request request;\n')
    s.write('Response response;\n')
    s.write('}; // struct %s\n'%(name))
    s.write('} // namespace %s\n\n'%(package))
    
    request_cpp_name = "Request"
    response_cpp_name = "Response"
    genmsg_cpp.write_traits(s, spec.request, package, request_cpp_name, cpp_prefix, datatype='%s/%sRequest'%(package, name))
    s.write('\n')
    genmsg_cpp.write_traits(s, spec.response, package, response_cpp_name, cpp_prefix, datatype='%s/%sResponse'%(package, name))
    genmsg_cpp.write_serialization(s, spec.request, package, request_cpp_name, cpp_prefix)
    s.write('\n')
    genmsg_cpp.write_serialization(s, spec.response, package, response_cpp_name, cpp_prefix)
    
    write_traits(s, spec, package, name, '%s::'%(package))
    
    write_end(s, package, name)
    
    output_dir = '%s/srv/cpp/%s'%(package_dir, package)
    if (not os.path.exists(output_dir)):
        os.makedirs(output_dir)
        
    f = open('%s/%s.h'%(output_dir, name), 'w')
    print >> f, s.getvalue()
    
    s.close()

def generate_services(argv):
    for arg in argv[1:]:
        generate(arg)

if __name__ == "__main__":
    roslib.msgs.set_verbose(False)
    generate_services(sys.argv)
