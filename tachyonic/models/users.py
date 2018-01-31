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
from uuid import uuid4

from luxon import database_model
from luxon import Models
from luxon import Uuid
from luxon import String
from luxon import Text
from luxon import DateTime
from luxon import Boolean
from luxon import Email
from luxon import Phone
from luxon import Enum
from luxon import Index
from luxon import ForeignKey
from luxon import UniqueIndex
from luxon.utils.timezone import now

ROLES = [
    ('00000000-0000-0000-0000-000000000000', 'Root', None, now()),
    (str(uuid4()), 'Operations', None, '0000-00-00 00:00:00'),
    (str(uuid4()), 'Administrator', None, '0000-00-00 00:00:00'),
    (str(uuid4()), 'Account Manager', None, '0000-00-00 00:00:00'),
    (str(uuid4()), 'Billing', None, '0000-00-00 00:00:00'),
    (str(uuid4()), 'Customer', None, '0000-00-00 00:00:00'),
    (str(uuid4()), 'Support', None, '0000-00-00 00:00:00'),
]

@database_model()
class role(Models):
    id = Uuid(default=uuid4)
    name = String(max_length=64)
    description = Text()
    creation_time = DateTime(default=now)
    primary_key = id
    unique_role = UniqueIndex(name)
    db_default_rows = ROLES
    roles = Index(name)


DOMAINS = [
    ('00000000-0000-0000-0000-000000000000', 'default', None, 1, now()),
]

@database_model()
class domain(Models):
    id = Uuid(default=uuid4)
    name = String(max_length=64)
    description = Text()
    enabled = Boolean(default=True)
    creation_time = DateTime(default=now)
    primary_key = id
    unique_domain = UniqueIndex(name)
    db_default_rows = DOMAINS
    domains = Index(name)

@database_model()
class tenant(Models):
    id = Uuid(default=uuid4)
    domain_id = Uuid()
    tenant_id = Uuid()
    name = String(max_length=100)
    enabled = Boolean(default=True)
    creation_time = DateTime(default=now)
    unique_tenant = UniqueIndex(domain_id, name)
    tenants = Index(id, domain_id)
    tenants_search_name = Index(domain_id, name)
    tenants_per_domain = Index(domain_id)
    primary_key = id


USERS = [
    ('00000000-0000-0000-0000-000000000000', 'tachyonic',
     '00000000-0000-0000-0000-000000000000', None,
     'root', '$2b$12$QaWa.Q3gZuafYXkPo3EJRuSJ1wGuutShb73RuH1gdUVri82CU6V5q',
     None, 'Default Root User', None, None, None, '0000-00-00 00:00:00',
     1, now()),
]

@database_model()
class user(Models):
    id = Uuid(default=uuid4)
    tag = String(max_length=30)
    domain_id = Uuid()
    tenant_id = Uuid()
    username = String(max_length=100)
    password = String(max_length=100)
    email = Email(max_length=255)
    name = String(max_length=100)
    phone_mobile = Phone()
    phone_office = Phone()
    designation = Enum('Mr','Mrs','Dr', 'Ms')
    last_login = DateTime()
    enabled = Boolean(default=True)
    creation_time = DateTime(default=now)
    unique_username = UniqueIndex(domain_id, username)
    user_tenant_ref = ForeignKey(tenant_id, tenant.id)
    user_domain_ref = ForeignKey(domain_id, domain.id)
    users = Index(domain_id, username)
    users_tenants = Index(domain_id, tenant_id)
    users_domain = Index(domain_id)
    primary_key = id
    db_default_rows = USERS


USER_ROLES = [
    ('00000000-0000-0000-0000-000000000000',
     '00000000-0000-0000-0000-000000000000',
     '00000000-0000-0000-0000-000000000000',
     None,
     '00000000-0000-0000-0000-000000000000',
     now()),
]

@database_model()
class user_role(Models):
    id = Uuid(default=uuid4)
    role_id = Uuid()
    domain_id = Uuid()
    tenant_id = String()
    user_id = Uuid()
    creation_time = DateTime(default=now)
    unique_user_role = UniqueIndex(role_id, tenant_id, user_id)
    user_role_id_ref = ForeignKey(role_id, role.id)
    user_role_domain_ref = ForeignKey(domain_id, domain.id)
    user_role_user_id_ref = ForeignKey(user_id, user.id)
    user_roles = Index(domain_id, tenant_id)
    primary_key = id
    db_default_rows = USER_ROLES
