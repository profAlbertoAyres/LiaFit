"""Testes do core.services.space_service."""

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from account.models import Organization, OrganizationMember, User
from core.models import SystemRole, UserSystemRole
from core.services.space_service import (
    KIND_ORG,
    KIND_PERSONAL,
    KIND_SAAS,
    get_user_spaces,
)


class GetUserSpacesTests(TestCase):

    def _make_user(self, email="user@test.com", is_superuser=False):
        return User.objects.create_user(
            email=email,
            password="x",
            is_superuser=is_superuser,
            is_staff=is_superuser,
        )

    def _make_org(self, name, slug, is_active=True, owner=None):
        return Organization.objects.create(
            company_name=name,
            slug=slug,
            is_active=is_active,
            owner=owner,
        )

    def _make_membership(self, user, org, is_active=True):
        return OrganizationMember.objects.create(
            user=user,
            organization=org,
            is_active=is_active,
        )

    def _make_saas_role(self, user):
        role = SystemRole.objects.create(
            name="SaaS Staff",
            scope=SystemRole.Scope.SUPERUSER,
            is_active=True,
        )
        return UserSystemRole.objects.create(
            user=user,
            system_role=role,
            is_active=True,
        )

    def test_user_sem_org_retorna_so_minha_area(self):
        user = self._make_user()
        spaces = get_user_spaces(user)
        self.assertEqual(len(spaces), 1)
        self.assertEqual(spaces[0]["kind"], KIND_PERSONAL)
        self.assertEqual(spaces[0]["name"], "Minha Área")

    def test_user_com_uma_org_ativa(self):
        user = self._make_user()
        org = self._make_org("Clínica ABC", "clinica-abc")
        self._make_membership(user, org)
        spaces = get_user_spaces(user)
        self.assertEqual(len(spaces), 2)
        self.assertEqual(spaces[1]["kind"], KIND_ORG)
        self.assertEqual(spaces[1]["key"], "org:clinica-abc")

    def test_orgs_em_ordem_alfabetica(self):
        user = self._make_user()
        for nome, slug in [("Clínica C", "c"), ("Clínica A", "a"), ("Clínica B", "b")]:
            self._make_membership(user, self._make_org(nome, slug))
        spaces = get_user_spaces(user)
        nomes = [s["name"] for s in spaces if s["kind"] == KIND_ORG]
        self.assertEqual(nomes, ["Clínica A", "Clínica B", "Clínica C"])

    def test_org_inativa_nao_aparece(self):
        user = self._make_user()
        self._make_membership(user, self._make_org("Ativa", "ativa", is_active=True))
        self._make_membership(user, self._make_org("Inativa", "inativa", is_active=False))
        spaces = get_user_spaces(user)
        nomes_org = [s["name"] for s in spaces if s["kind"] == KIND_ORG]
        self.assertEqual(nomes_org, ["Ativa"])

    def test_membership_inativo_nao_aparece(self):
        user = self._make_user()
        org = self._make_org("Clínica", "clinica")
        self._make_membership(user, org, is_active=False)
        spaces = get_user_spaces(user)
        self.assertNotIn(KIND_ORG, [s["kind"] for s in spaces])

    def test_saas_staff_nao_superuser(self):
        user = self._make_user(is_superuser=False)
        self._make_saas_role(user)
        spaces = get_user_spaces(user)
        self.assertEqual([s["kind"] for s in spaces], [KIND_PERSONAL, KIND_SAAS])

    def test_superuser_recebe_saas(self):
        user = self._make_user(email="root@test.com", is_superuser=True)
        spaces = get_user_spaces(user)
        self.assertEqual([s["kind"] for s in spaces], [KIND_PERSONAL, KIND_SAAS])

    def test_saas_staff_com_orgs(self):
        user = self._make_user(is_superuser=True)
        self._make_membership(user, self._make_org("Beta", "beta", owner=user))
        self._make_membership(user, self._make_org("Alpha", "alpha", owner=user))
        spaces = get_user_spaces(user)
        kinds = [s["kind"] for s in spaces]
        self.assertEqual(kinds, [KIND_PERSONAL, KIND_ORG, KIND_ORG, KIND_SAAS])
        org_names = [s["name"] for s in spaces if s["kind"] == KIND_ORG]
        self.assertEqual(org_names, ["Alpha", "Beta"])

    def test_anonymous_user_retorna_vazio(self):
        self.assertEqual(get_user_spaces(AnonymousUser()), [])
        self.assertEqual(get_user_spaces(None), [])
