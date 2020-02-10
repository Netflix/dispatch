def test_resource_union(session, document, individual_contact, team_contact):
    from dispatch.route.service import resource_union
    from .factories import DocumentFactory

    unions = resource_union([individual_contact, team_contact, document], 1)
    assert len(unions) == 3

    docs = [DocumentFactory() for x in range(3)]
    resources = docs + [individual_contact, team_contact]
    unions = resource_union(resources, 3)
    assert len(unions) == 0

    resources = [individual_contact, individual_contact, team_contact, document]
    unions = resource_union(resources, 2)
    assert len(unions) == 1
    assert unions[0] == individual_contact

    resources = [individual_contact, individual_contact]
    unions = resource_union(resources, 2)
    assert len(unions) == 1
    assert unions[0] == individual_contact
