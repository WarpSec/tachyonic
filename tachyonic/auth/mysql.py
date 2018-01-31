# -*- coding: utf-8 -*-
# Copyright (c) 2018 Christiaan Frans Rademan.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holders nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
from luxon import db
from luxon.core.auth.driver import BaseDriver
from luxon.utils.password import valid as is_valid_password

class Mysql(BaseDriver):
    def authenticate(self, username, password, domain='default'):
        with db() as conn:
            crsr = conn.execute('SELECT user.id AS user_id' +
                                ' ,user.email AS email' +
                                ' ,user.name AS name' +
                                ' ,user.last_login AS last_login' +
                                ' ,user.username AS username' +
                                ' ,user.password AS password' +
                                ' ,user_domain.name AS domain' +
                                ' ,user_domain.id AS domain_id' +
                                ' ,user.tenant_id AS tenant_id' +
                                ' ,user_tenant.name AS tenant' +
                                ' ,user_role.role_id AS role_id' +
                                ' ,user_role.domain_id AS role_domain_id' +
                                ' ,role_domain.name AS role_domain' +
                                ' ,user_role.tenant_id AS role_tenant_id' +
                                ' ,role_tenant.name AS role_tenant' +
                                ' ,role_tenant.enabled AS role_tenant_enabled' +
                                ' ,role.name AS role_name' +
                                ' FROM user' +
                                ' LEFT JOIN user_role' +
                                ' ON user.id = user_role.user_id' +
                                ' LEFT JOIN domain as user_domain' +
                                ' ON user.domain_id = user_domain.id' +
                                ' LEFT JOIN tenant as user_tenant' +
                                ' ON user.tenant_id = user_tenant.id' +
                                ' LEFT JOIN tenant as role_tenant' +
                                ' ON user_role.tenant_id = role_tenant.id' +
                                ' LEFT JOIN domain as role_domain' +
                                ' ON user_role.domain_id = role_domain.id' +
                                ' LEFT JOIN role' +
                                ' ON user_role.role_id = role.id' +
                                ' WHERE user.enabled = 1' +
                                ' AND user_domain.enabled = 1' +
                                ' AND role_domain.enabled = 1' +
                                ' AND (user_tenant.enabled = 1' +
                                ' OR user_tenant.enabled is NULL)' +
                                ' AND user.username = %s' +
                                ' AND user_domain.name = %s',
                                (username, domain))
            result = crsr.fetchall()
            if len(result) > 0:
                # Validate Password againts stored HASHED Value.
                if is_valid_password(password, result[0]['password']):

                    roles = []
                    for role in result:
                        if (role['role_id'] is not None and
                                (role['role_tenant_id'] is None or
                                 role['role_tenant_enabled'] == 1)):
                            roles.append((role['role_name'],
                                          role['role_domain'],
                                          role['role_tenant_id']))

                    self.new_token(user_id=result[0]['user_id'],
                                   username=username,
                                   domain=domain,
                                   domain_id=result[0]['domain_id'],
                                   tenant_id=result[0]['tenant_id'],
                                   roles=roles)
                    return True

            return False
