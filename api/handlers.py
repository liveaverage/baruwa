#
# Baruwa
# Copyright (C) 2010  Andrew Colin Kissa
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
from piston.handler import BaseHandler
from piston.utils import validate
from baruwa.messages.models import Maillog
from baruwa.messages.forms import QuarantineProcessForm
from baruwa.messages.views import process_quarantined_msg,index,preview

class MessagesHandler(BaseHandler):
    model = Maillog
    exclude = ()
    allowed_methods = ('GET')

    def read(self,request,list_all=0,page=1,quarantine=0,direction='dsc',order_by='timestamp'):
        json = index(request,list_all,page,quarantine,direction,order_by,True)
        return json

class MessageProcess(BaseHandler):
    allowed_methods = ('POST')

    @validate(QuarantineProcessForm,'POST')
    def update(self,request):
        request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        json = process_quarantined_msg(request)
        return json

class MessagePreview(BaseHandler):
    allowed_methods = ('GET')

    def read(self,request,message_id):
        request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        json = preview(request,message_id)
        return json
