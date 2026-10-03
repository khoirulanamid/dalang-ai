"""
test_wayang_directory.py

Pengujian unit dan integrasi untuk modul direktori kantor Dalang-AI.
Menguji validitas seluruh 12 profil Wayang, penegakan invariant DDD,
dan fungsionalitas pencarian pada aggregate WayangDirectory.
"""

from datetime import datetime, timezone
import pytest

from wayang_directory import (
    AgentRole,
    AvailabilityStatus,
    ContactHandle,
    ExpertiseDomain,
    TaskDomain,
    WayangDirectory,
    WayangId,
    WayangProfile,
    WayangPublicSummary,
    build_dalang_directory,
    get_directory,
)


EXPECTED_WAYANG_IDS = {
    "kai",
    "zaki",
    "ren",
    "pingot",
    "nova",
    "tara",
    "deva",
    "sari",
    "vino",
    "lena",
    "riko",
    "doku",
}


class TestWayangDirectoryCompleteness:
    """Verifikasi bahwa direktori memuat tepat 12 Wayang resmi."""

    def test_directory_has_exactly_12_profiles(self) -> None:
        directory = build_dalang_directory()
        assert directory.count() == 12

    def test_all_expected_ids_present(self) -> None:
        directory = build_dalang_directory()
        registered_ids = {str(p.wayang_id) for p in directory.all_profiles()}
        assert registered_ids == EXPECTED_WAYANG_IDS

    @pytest.mark.parametrize("wayang_id", sorted(EXPECTED_WAYANG_IDS))
    def test_each_profile_has_complete_required_fields(self, wayang_id: str) -> None:
        directory = build_dalang_directory()
        profile = directory.find_by_id(wayang_id)

        assert str(profile.wayang_id) == wayang_id
        assert len(profile.display_name.strip()) > 0
        assert isinstance(profile.role, AgentRole)
        assert len(profile.expertise_domains) >= 3, "Wayang harus punya minimal 3 keahlian"
        assert len(profile.task_domains) >= 2, "Wayang harus punya minimal 2 domain tugas"
        assert len(profile.primary_tools) >= 2, "Wayang harus punya minimal 2 alat utama"
        assert str(profile.contact_handle) == f"@{wayang_id}"
        assert isinstance(profile.availability, AvailabilityStatus)
        assert profile.registered_at.tzinfo == timezone.utc


class TestValueObjectInvariants:
    """Verifikasi validasi invariant pada setiap Value Object."""

    def test_wayang_id_valid_format(self) -> None:
        valid_id = WayangId("kai")
        assert str(valid_id) == "kai"

    @pytest.mark.parametrize(
        "invalid_id",
        ["", "1kai", "Kai", "kai-agent", "k", "a" * 33, "@kai"],
    )
    def test_wayang_id_rejects_invalid_patterns(self, invalid_id: str) -> None:
        with pytest.raises(ValueError, match="WayangId .* tidak valid"):
            WayangId(invalid_id)

    def test_contact_handle_valid(self) -> None:
        handle = ContactHandle("@zaki")
        assert str(handle) == "@zaki"

    @pytest.mark.parametrize(
        "invalid_handle",
        ["zaki", "@@zaki", "@", "@1zaki", "@zaki-dev"],
    )
    def test_contact_handle_rejects_malformed_pattern(self, invalid_handle: str) -> None:
        with pytest.raises(ValueError, match="ContactHandle .* tidak valid"):
            ContactHandle(invalid_handle)

    def test_expertise_domain_strips_whitespace(self) -> None:
        expertise = ExpertiseDomain("  FastAPI  ")
        assert str(expertise) == "FastAPI"

    def test_expertise_domain_rejects_empty(self) -> None:
        with pytest.raises(ValueError, match="tidak boleh kosong"):
            ExpertiseDomain("   ")

    def test_task_domain_rejects_empty(self) -> None:
        with pytest.raises(ValueError, match="tidak boleh kosong"):
            TaskDomain("")


class TestProfileInvariants:
    """Verifikasi invariant pada level Entity WayangProfile."""

    def test_rejects_empty_display_name(self) -> None:
        with pytest.raises(ValueError, match="display_name tidak boleh kosong"):
            WayangProfile(
                wayang_id=WayangId("test"),
                display_name="",
                role=AgentRole.BACKEND_ENGINEER,
                expertise_domains=frozenset([ExpertiseDomain("Python")]),
                task_domains=frozenset([TaskDomain("API")]),
                primary_tools=frozenset(["pytest"]),
                contact_handle=ContactHandle("@test"),
                availability=AvailabilityStatus.ACTIVE,
                registered_at=datetime.now(timezone.utc),
            )

    def test_rejects_empty_expertise(self) -> None:
        with pytest.raises(ValueError, match="minimal satu ExpertiseDomain"):
            WayangProfile(
                wayang_id=WayangId("test"),
                display_name="Test Agent",
                role=AgentRole.BACKEND_ENGINEER,
                expertise_domains=frozenset(),
                task_domains=frozenset([TaskDomain("API")]),
                primary_tools=frozenset(["pytest"]),
                contact_handle=ContactHandle("@test"),
                availability=AvailabilityStatus.ACTIVE,
                registered_at=datetime.now(timezone.utc),
            )

    def test_rejects_mismatched_contact_handle(self) -> None:
        with pytest.raises(ValueError, match="tidak sesuai dengan wayang_id"):
            WayangProfile(
                wayang_id=WayangId("test"),
                display_name="Test Agent",
                role=AgentRole.BACKEND_ENGINEER,
                expertise_domains=frozenset([ExpertiseDomain("Python")]),
                task_domains=frozenset([TaskDomain("API")]),
                primary_tools=frozenset(["pytest"]),
                contact_handle=ContactHandle("@other"),
                availability=AvailabilityStatus.ACTIVE,
                registered_at=datetime.now(timezone.utc),
            )

    def test_rejects_naive_datetime(self) -> None:
        with pytest.raises(ValueError, match="timezone-aware"):
            WayangProfile(
                wayang_id=WayangId("test"),
                display_name="Test Agent",
                role=AgentRole.BACKEND_ENGINEER,
                expertise_domains=frozenset([ExpertiseDomain("Python")]),
                task_domains=frozenset([TaskDomain("API")]),
                primary_tools=frozenset(["pytest"]),
                contact_handle=ContactHandle("@test"),
                availability=AvailabilityStatus.ACTIVE,
                registered_at=datetime(2025, 1, 1),  # Naive, no tzinfo
            )


class TestWayangDirectoryOperations:
    """Verifikasi metode query dan invariant dari WayangDirectory."""

    def test_find_by_id_found(self) -> None:
        directory = build_dalang_directory()
        kai = directory.find_by_id("kai")
        assert kai.role == AgentRole.ORCHESTRATOR
        assert kai.display_name.startswith("Kai")

    def test_find_by_id_not_found_raises_key_error(self) -> None:
        directory = build_dalang_directory()
        with pytest.raises(KeyError, match="tidak ditemukan"):
            directory.find_by_id("unknown_agent")

    def test_find_by_role(self) -> None:
        directory = build_dalang_directory()
        orchestrators = directory.find_by_role(AgentRole.ORCHESTRATOR)
        assert len(orchestrators) == 1
        assert str(orchestrators[0].wayang_id) == "kai"

    def test_find_by_expertise(self) -> None:
        directory = build_dalang_directory()
        # Pingot dan Zaki keduanya punya keahlian PostgreSQL
        pg_experts = directory.find_by_expertise("PostgreSQL")
        expert_ids = {str(p.wayang_id) for p in pg_experts}
        assert "pingot" in expert_ids
        assert "zaki" in expert_ids

    def test_duplicate_registration_rejected(self) -> None:
        directory = build_dalang_directory()
        duplicate_kai = directory.find_by_id("kai")
        with pytest.raises(ValueError, match="sudah terdaftar"):
            directory.register(duplicate_kai)

    def test_public_roster_projection(self) -> None:
        directory = build_dalang_directory()
        roster = directory.public_roster()
        assert len(roster) == 12

        sample = roster[0]
        assert isinstance(sample, WayangPublicSummary)
        assert isinstance(sample.wayang_id, str)
        assert isinstance(sample.expertise_domains, tuple)
        assert isinstance(sample.primary_tools, tuple)
        assert sample.registered_at.endswith("Z")

    def test_singleton_returns_same_instance(self) -> None:
        dir1 = get_directory()
        dir2 = get_directory()
        assert dir1 is dir2
        assert dir1.count() == 12
