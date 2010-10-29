#include <QtTest/QtTest>

#include <TelepathyQt4/RequestableChannelClassSpec>

using namespace Tp;

class TestRCCSpec : public QObject
{
    Q_OBJECT

private Q_SLOTS:
    void testRCCSpec();
};

void TestRCCSpec::testRCCSpec()
{
    RequestableChannelClassSpec spec;

    spec = RequestableChannelClassSpec::textChat();
    QCOMPARE(spec.channelType(), TP_QT4_IFACE_CHANNEL_TYPE_TEXT);
    QCOMPARE(spec.targetHandleType(), static_cast<uint>(HandleTypeContact));
    QCOMPARE(spec.fixedProperties().size(), 2);
    QCOMPARE(spec.allowedProperties().isEmpty(), true);

    spec = RequestableChannelClassSpec::textChatroom();
    QCOMPARE(spec.channelType(), TP_QT4_IFACE_CHANNEL_TYPE_TEXT);
    QCOMPARE(spec.targetHandleType(), static_cast<uint>(HandleTypeRoom));
    QCOMPARE(spec.fixedProperties().size(), 2);
    QCOMPARE(spec.allowedProperties().isEmpty(), true);

    spec = RequestableChannelClassSpec::mediaCall();
    QCOMPARE(spec.channelType(), TP_QT4_IFACE_CHANNEL_TYPE_STREAMED_MEDIA);
    QCOMPARE(spec.targetHandleType(), static_cast<uint>(HandleTypeContact));
    QCOMPARE(spec.fixedProperties().size(), 2);
    QCOMPARE(spec.allowedProperties().isEmpty(), true);

    spec = RequestableChannelClassSpec::audioCall();
    QCOMPARE(spec.channelType(), TP_QT4_IFACE_CHANNEL_TYPE_STREAMED_MEDIA);
    QCOMPARE(spec.targetHandleType(), static_cast<uint>(HandleTypeContact));
    QCOMPARE(spec.fixedProperties().size(), 2);
    QCOMPARE(spec.allowedProperties().size(), 1);
    QCOMPARE(spec.allowsProperty(TP_QT4_IFACE_CHANNEL_TYPE_STREAMED_MEDIA + QLatin1String(".InitialAudio")), true);

    spec = RequestableChannelClassSpec::videoCall();
    QCOMPARE(spec.channelType(), TP_QT4_IFACE_CHANNEL_TYPE_STREAMED_MEDIA);
    QCOMPARE(spec.targetHandleType(), static_cast<uint>(HandleTypeContact));
    QCOMPARE(spec.fixedProperties().size(), 2);
    QCOMPARE(spec.allowedProperties().size(), 1);
    QCOMPARE(spec.allowsProperty(TP_QT4_IFACE_CHANNEL_TYPE_STREAMED_MEDIA + QLatin1String(".InitialVideo")), true);

    spec = RequestableChannelClassSpec::videoCallWithAudio();
    QCOMPARE(spec.channelType(), TP_QT4_IFACE_CHANNEL_TYPE_STREAMED_MEDIA);
    QCOMPARE(spec.targetHandleType(), static_cast<uint>(HandleTypeContact));
    QCOMPARE(spec.fixedProperties().size(), 2);
    QCOMPARE(spec.allowedProperties().size(), 2);
    QCOMPARE(spec.allowsProperty(TP_QT4_IFACE_CHANNEL_TYPE_STREAMED_MEDIA + QLatin1String(".InitialAudio")), true);
    QCOMPARE(spec.allowsProperty(TP_QT4_IFACE_CHANNEL_TYPE_STREAMED_MEDIA + QLatin1String(".InitialVideo")), true);

    spec = RequestableChannelClassSpec::conferenceTextChat();
    QCOMPARE(spec.channelType(), TP_QT4_IFACE_CHANNEL_TYPE_TEXT);
    QCOMPARE(spec.targetHandleType(), static_cast<uint>(HandleTypeContact));
    QCOMPARE(spec.fixedProperties().size(), 2);
    QCOMPARE(spec.allowedProperties().size(), 1);
    QCOMPARE(spec.allowsProperty(TP_QT4_IFACE_CHANNEL_INTERFACE_CONFERENCE + QLatin1String(".InitialChannels")), true);

    spec = RequestableChannelClassSpec::conferenceTextChatWithInvitees();
    QCOMPARE(spec.channelType(), TP_QT4_IFACE_CHANNEL_TYPE_TEXT);
    QCOMPARE(spec.targetHandleType(), static_cast<uint>(HandleTypeContact));
    QCOMPARE(spec.fixedProperties().size(), 2);
    QCOMPARE(spec.allowedProperties().size(), 2);
    QCOMPARE(spec.allowsProperty(TP_QT4_IFACE_CHANNEL_INTERFACE_CONFERENCE + QLatin1String(".InitialChannels")), true);
    QCOMPARE(spec.allowsProperty(TP_QT4_IFACE_CHANNEL_INTERFACE_CONFERENCE + QLatin1String(".InitialInviteeHandles")), true);

    spec = RequestableChannelClassSpec::conferenceTextChatroom();
    QCOMPARE(spec.channelType(), TP_QT4_IFACE_CHANNEL_TYPE_TEXT);
    QCOMPARE(spec.targetHandleType(), static_cast<uint>(HandleTypeRoom));
    QCOMPARE(spec.fixedProperties().size(), 2);
    QCOMPARE(spec.allowedProperties().size(), 1);
    QCOMPARE(spec.allowsProperty(TP_QT4_IFACE_CHANNEL_INTERFACE_CONFERENCE + QLatin1String(".InitialChannels")), true);

    spec = RequestableChannelClassSpec::conferenceTextChatroomWithInvitees();
    QCOMPARE(spec.channelType(), TP_QT4_IFACE_CHANNEL_TYPE_TEXT);
    QCOMPARE(spec.targetHandleType(), static_cast<uint>(HandleTypeRoom));
    QCOMPARE(spec.fixedProperties().size(), 2);
    QCOMPARE(spec.allowedProperties().size(), 2);
    QCOMPARE(spec.allowsProperty(TP_QT4_IFACE_CHANNEL_INTERFACE_CONFERENCE + QLatin1String(".InitialChannels")), true);
    QCOMPARE(spec.allowsProperty(TP_QT4_IFACE_CHANNEL_INTERFACE_CONFERENCE + QLatin1String(".InitialInviteeHandles")), true);

    spec = RequestableChannelClassSpec::conferenceMediaCall();
    QCOMPARE(spec.channelType(), TP_QT4_IFACE_CHANNEL_TYPE_STREAMED_MEDIA);
    QCOMPARE(spec.targetHandleType(), static_cast<uint>(HandleTypeContact));
    QCOMPARE(spec.fixedProperties().size(), 2);
    QCOMPARE(spec.allowedProperties().size(), 1);
    QCOMPARE(spec.allowsProperty(TP_QT4_IFACE_CHANNEL_INTERFACE_CONFERENCE + QLatin1String(".InitialChannels")), true);

    spec = RequestableChannelClassSpec::conferenceMediaCallWithInvitees();
    QCOMPARE(spec.channelType(), TP_QT4_IFACE_CHANNEL_TYPE_STREAMED_MEDIA);
    QCOMPARE(spec.targetHandleType(), static_cast<uint>(HandleTypeContact));
    QCOMPARE(spec.fixedProperties().size(), 2);
    QCOMPARE(spec.allowedProperties().size(), 2);
    QCOMPARE(spec.allowsProperty(TP_QT4_IFACE_CHANNEL_INTERFACE_CONFERENCE + QLatin1String(".InitialChannels")), true);
    QCOMPARE(spec.allowsProperty(TP_QT4_IFACE_CHANNEL_INTERFACE_CONFERENCE + QLatin1String(".InitialInviteeHandles")), true);

    spec = RequestableChannelClassSpec::contactSearch();
    QCOMPARE(spec.channelType(), TP_QT4_IFACE_CHANNEL_TYPE_CONTACT_SEARCH);
    QCOMPARE(spec.fixedProperties().size(), 1);
    QCOMPARE(spec.allowedProperties().isEmpty(), true);

    spec = RequestableChannelClassSpec::contactSearchWithSpecificServer();
    QCOMPARE(spec.channelType(), TP_QT4_IFACE_CHANNEL_TYPE_CONTACT_SEARCH);
    QCOMPARE(spec.fixedProperties().size(), 1);
    QCOMPARE(spec.allowedProperties().size(), 1);
    QCOMPARE(spec.allowsProperty(TP_QT4_IFACE_CHANNEL_TYPE_CONTACT_SEARCH + QLatin1String(".Server")), true);

    spec = RequestableChannelClassSpec::contactSearchWithLimit();
    QCOMPARE(spec.channelType(), TP_QT4_IFACE_CHANNEL_TYPE_CONTACT_SEARCH);
    QCOMPARE(spec.fixedProperties().size(), 1);
    QCOMPARE(spec.allowedProperties().size(), 1);
    QCOMPARE(spec.allowsProperty(TP_QT4_IFACE_CHANNEL_TYPE_CONTACT_SEARCH + QLatin1String(".Limit")), true);

    spec = RequestableChannelClassSpec::contactSearchWithSpecificServerAndLimit();
    QCOMPARE(spec.channelType(), TP_QT4_IFACE_CHANNEL_TYPE_CONTACT_SEARCH);
    QCOMPARE(spec.fixedProperties().size(), 1);
    QCOMPARE(spec.allowedProperties().size(), 2);
    QCOMPARE(spec.allowsProperty(TP_QT4_IFACE_CHANNEL_TYPE_CONTACT_SEARCH + QLatin1String(".Server")), true);
    QCOMPARE(spec.allowsProperty(TP_QT4_IFACE_CHANNEL_TYPE_CONTACT_SEARCH + QLatin1String(".Limit")), true);

    QCOMPARE(RequestableChannelClassSpec::videoCallWithAudio().supports(RequestableChannelClassSpec::videoCall()), true);
    QCOMPARE(RequestableChannelClassSpec::videoCallWithAudio().supports(RequestableChannelClassSpec::audioCall()), true);
    QCOMPARE(RequestableChannelClassSpec::videoCallWithAudio().supports(RequestableChannelClassSpec::mediaCall()), true);

    QCOMPARE(RequestableChannelClassSpec::textChat() == RequestableChannelClassSpec::textChatroom(), false);

    RequestableChannelClass rcc;
    rcc.fixedProperties.insert(TP_QT4_IFACE_CHANNEL + QLatin1String(".ChannelType"),
            TP_QT4_IFACE_CHANNEL_TYPE_TEXT);
    rcc.fixedProperties.insert(TP_QT4_IFACE_CHANNEL + QLatin1String(".TargetHandleType"),
            (uint) HandleTypeContact);
    spec = RequestableChannelClassSpec(rcc);
    QCOMPARE(RequestableChannelClassSpec::textChat() == spec, true);
}

QTEST_MAIN(TestRCCSpec)
#include "_gen/rccspec.cpp.moc.hpp"
