/**
 * This file is part of TelepathyQt
 *
 * @copyright Copyright (C) 2009-2010 Collabora Ltd. <http://www.collabora.co.uk/>
 * @copyright Copyright (C) 2009-2010 Nokia Corporation
 * @license LGPL 2.1
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

#ifndef _TelepathyQt_connection_capabilities_h_HEADER_GUARD_
#define _TelepathyQt_connection_capabilities_h_HEADER_GUARD_

#ifndef IN_TP_QT_HEADER
#error IN_TP_QT_HEADER
#endif

#include <TelepathyQt/CapabilitiesBase>
#include <TelepathyQt/Types>

namespace Tp
{

class TestBackdoors;

class TP_QT_EXPORT ConnectionCapabilities : public CapabilitiesBase
{
public:
    ConnectionCapabilities();
    virtual ~ConnectionCapabilities();

    bool textChatrooms() const;

    bool conferenceStreamedMediaCalls() const;
    bool conferenceStreamedMediaCallsWithInvitees() const;
    bool conferenceTextChats() const;
    bool conferenceTextChatsWithInvitees() const;
    bool conferenceTextChatrooms() const;
    bool conferenceTextChatroomsWithInvitees() const;

    bool contactSearches() const;
    bool contactSearchesWithSpecificServer() const;
    bool contactSearchesWithLimit() const;

    bool streamTubes() const;

protected:
    friend class Account;
    friend class Connection;
    friend class ProtocolInfo;
    friend class TestBackdoors;

    ConnectionCapabilities(const RequestableChannelClassList &rccs);
    ConnectionCapabilities(const RequestableChannelClassSpecList &rccSpecs);
};

} // Tp

Q_DECLARE_METATYPE(Tp::ConnectionCapabilities);

#endif
