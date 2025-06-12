from typing import Any, Optional

from sqlalchemy import BigInteger, Boolean, CheckConstraint, Column, DateTime, Double, Index, Integer, Numeric, PrimaryKeyConstraint, SmallInteger, String, Table, Text, UniqueConstraint, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB, OID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql.sqltypes import NullType
import datetime
import uuid

class Base(DeclarativeBase):
    pass


class ActionItems(Base):
    __tablename__ = 'action_items'
    __table_args__ = (
        CheckConstraint("status = ANY (ARRAY['未着手'::text, '進行中'::text, '完了'::text, '保留'::text, '中止'::text])", name='check_status'),
        PrimaryKeyConstraint('action_item_id', name='action_items_pkey')
    )

    action_item_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    talk_session_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    sequence: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class AuthStates(Base):
    __tablename__ = 'auth_states'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='auth_states_pkey'),
        UniqueConstraint('state', name='auth_states_state_key'),
        Index('idx_auth_states_expires_at', 'expires_at'),
        Index('idx_auth_states_state', 'state')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    state: Mapped[str] = mapped_column(String(255))
    provider: Mapped[str] = mapped_column(String(50))
    redirect_url: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime(True))
    registration_url: Mapped[Optional[str]] = mapped_column(String(255))


t_geography_columns = Table(
    'geography_columns', Base.metadata,
    Column('f_table_catalog', String),
    Column('f_table_schema', String),
    Column('f_table_name', String),
    Column('f_geography_column', String),
    Column('coord_dimension', Integer),
    Column('srid', Integer),
    Column('type', Text)
)


t_geometry_columns = Table(
    'geometry_columns', Base.metadata,
    Column('f_table_catalog', String(256)),
    Column('f_table_schema', String),
    Column('f_table_name', String),
    Column('f_geometry_column', String),
    Column('coord_dimension', Integer),
    Column('srid', Integer),
    Column('type', String(30))
)


class OpinionReports(Base):
    __tablename__ = 'opinion_reports'
    __table_args__ = (
        PrimaryKeyConstraint('opinion_report_id', name='opinion_reports_pkey'),
        Index('opinion_reports_opinion_id_idx', 'opinion_id'),
        Index('opinion_reports_talk_session_id_idx', 'talk_session_id')
    )

    opinion_report_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    opinion_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    talk_session_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    reporter_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    reason: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), server_default=text("'unconfirmed'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    reason_text: Mapped[Optional[str]] = mapped_column(Text)


class Opinions(Base):
    __tablename__ = 'opinions'
    __table_args__ = (
        PrimaryKeyConstraint('opinion_id', name='opinions_pkey'),
        Index('idx_opinions_opinion_id_parent_opinion_id', 'opinion_id', 'parent_opinion_id'),
        Index('idx_opinions_parent_opinion_id', 'parent_opinion_id'),
        Index('idx_opinions_talk_session_id', 'talk_session_id'),
        Index('idx_opinions_user_id', 'user_id')
    )

    opinion_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    talk_session_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    content: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('now()'))
    parent_opinion_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    title: Mapped[Optional[str]] = mapped_column(String)
    picture_url: Mapped[Optional[str]] = mapped_column(String)
    reference_url: Mapped[Optional[str]] = mapped_column(String)


class OrganizationUsers(Base):
    __tablename__ = 'organization_users'
    __table_args__ = (
        PrimaryKeyConstraint('organization_user_id', name='organization_users_pkey'),
    )

    organization_user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    role: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class Organizations(Base):
    __tablename__ = 'organizations'
    __table_args__ = (
        PrimaryKeyConstraint('organization_id', name='organizations_pkey'),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    organization_type: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(255))
    owner_id: Mapped[uuid.UUID] = mapped_column(Uuid)


class PasswordAuth(Base):
    __tablename__ = 'password_auth'
    __table_args__ = (
        PrimaryKeyConstraint('password_auth_id', name='password_auth_pkey'),
        UniqueConstraint('user_id', name='password_auth_user_id_key'),
        Index('idx_password_auth_user_id', 'user_id')
    )

    password_auth_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    password_hash: Mapped[str] = mapped_column(String(255))
    last_changed: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    salt: Mapped[Optional[str]] = mapped_column(String(255))


t_pg_stat_statements = Table(
    'pg_stat_statements', Base.metadata,
    Column('userid', OID),
    Column('dbid', OID),
    Column('toplevel', Boolean),
    Column('queryid', BigInteger),
    Column('query', Text),
    Column('plans', BigInteger),
    Column('total_plan_time', Double(53)),
    Column('min_plan_time', Double(53)),
    Column('max_plan_time', Double(53)),
    Column('mean_plan_time', Double(53)),
    Column('stddev_plan_time', Double(53)),
    Column('calls', BigInteger),
    Column('total_exec_time', Double(53)),
    Column('min_exec_time', Double(53)),
    Column('max_exec_time', Double(53)),
    Column('mean_exec_time', Double(53)),
    Column('stddev_exec_time', Double(53)),
    Column('rows', BigInteger),
    Column('shared_blks_hit', BigInteger),
    Column('shared_blks_read', BigInteger),
    Column('shared_blks_dirtied', BigInteger),
    Column('shared_blks_written', BigInteger),
    Column('local_blks_hit', BigInteger),
    Column('local_blks_read', BigInteger),
    Column('local_blks_dirtied', BigInteger),
    Column('local_blks_written', BigInteger),
    Column('temp_blks_read', BigInteger),
    Column('temp_blks_written', BigInteger),
    Column('blk_read_time', Double(53)),
    Column('blk_write_time', Double(53)),
    Column('temp_blk_read_time', Double(53)),
    Column('temp_blk_write_time', Double(53)),
    Column('wal_records', BigInteger),
    Column('wal_fpi', BigInteger),
    Column('wal_bytes', Numeric),
    Column('jit_functions', BigInteger),
    Column('jit_generation_time', Double(53)),
    Column('jit_inlining_count', BigInteger),
    Column('jit_inlining_time', Double(53)),
    Column('jit_optimization_count', BigInteger),
    Column('jit_optimization_time', Double(53)),
    Column('jit_emission_count', BigInteger),
    Column('jit_emission_time', Double(53))
)


t_pg_stat_statements_info = Table(
    'pg_stat_statements_info', Base.metadata,
    Column('dealloc', BigInteger),
    Column('stats_reset', DateTime(True))
)


class PolicyConsents(Base):
    __tablename__ = 'policy_consents'
    __table_args__ = (
        PrimaryKeyConstraint('policy_consent_id', name='policy_consents_pkey'),
        Index('idx_user_policy', 'user_id', 'policy_version')
    )

    policy_consent_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    policy_version: Mapped[str] = mapped_column(String(20))
    consented_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    ip_address: Mapped[str] = mapped_column(String(45))
    user_agent: Mapped[str] = mapped_column(Text)


class PolicyVersions(Base):
    __tablename__ = 'policy_versions'
    __table_args__ = (
        PrimaryKeyConstraint('version', name='policy_versions_pkey'),
        Index('idx_version_created_at', 'version', 'created_at')
    )

    version: Mapped[str] = mapped_column(String(20), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class RepresentativeOpinions(Base):
    __tablename__ = 'representative_opinions'
    __table_args__ = (
        PrimaryKeyConstraint('talk_session_id', 'opinion_id', 'group_id', name='representative_opinions_pkey'),
    )

    talk_session_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    opinion_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    group_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rank: Mapped[int] = mapped_column(Integer)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('now()'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('now()'))
    agree_count: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    disagree_count: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    pass_count: Mapped[int] = mapped_column(Integer, server_default=text('0'))


class SchemaMigrations(Base):
    __tablename__ = 'schema_migrations'
    __table_args__ = (
        PrimaryKeyConstraint('version', name='schema_migrations_pkey'),
    )

    version: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    dirty: Mapped[bool] = mapped_column(Boolean)


class Sessions(Base):
    __tablename__ = 'sessions'
    __table_args__ = (
        PrimaryKeyConstraint('session_id', name='sessions_pkey'),
        Index('idx_session_id_user_id', 'user_id', 'session_id')
    )

    session_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    provider: Mapped[str] = mapped_column(String)
    session_status: Mapped[int] = mapped_column(Integer)
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('now()'))
    last_activity_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('now()'))


class SpatialRefSys(Base):
    __tablename__ = 'spatial_ref_sys'
    __table_args__ = (
        CheckConstraint('srid > 0 AND srid <= 998999', name='spatial_ref_sys_srid_check'),
        PrimaryKeyConstraint('srid', name='spatial_ref_sys_pkey')
    )

    srid: Mapped[int] = mapped_column(Integer, primary_key=True)
    auth_name: Mapped[Optional[str]] = mapped_column(String(256))
    auth_srid: Mapped[Optional[int]] = mapped_column(Integer)
    srtext: Mapped[Optional[str]] = mapped_column(String(2048))
    proj4text: Mapped[Optional[str]] = mapped_column(String(2048))


class TalkSessionConclusions(Base):
    __tablename__ = 'talk_session_conclusions'
    __table_args__ = (
        PrimaryKeyConstraint('talk_session_id', name='talk_session_conclusions_pkey'),
        Index('idx_talk_session_conclusions_creator', 'created_by'),
        Index('idx_talk_session_conclusions_talk_session_id', 'talk_session_id')
    )

    talk_session_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class TalkSessionGeneratedImages(Base):
    __tablename__ = 'talk_session_generated_images'
    __table_args__ = (
        PrimaryKeyConstraint('talk_session_id', name='talk_session_generated_images_pkey'),
    )

    talk_session_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    wordmap_url: Mapped[str] = mapped_column(Text)
    tsnc_url: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('now()'))


# class TalkSessionLocations(Base):
#     __tablename__ = 'talk_session_locations'
#     __table_args__ = (
#         PrimaryKeyConstraint('talk_session_id', name='talk_session_locations_pkey'),
#         Index('idx_talk_session_locations_geography', 'location')
#     )

#     talk_session_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
#     location: Mapped[Any] = mapped_column(NullType)


class TalkSessionReportHistories(Base):
    __tablename__ = 'talk_session_report_histories'
    __table_args__ = (
        PrimaryKeyConstraint('talk_session_report_history_id', name='talk_session_report_histories_pkey'),
    )

    talk_session_report_history_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    talk_session_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    report: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('now()'))


class TalkSessionReports(Base):
    __tablename__ = 'talk_session_reports'
    __table_args__ = (
        PrimaryKeyConstraint('talk_session_id', name='talk_session_reports_pkey'),
        Index('talk_session_report_talk_session_id_index', 'talk_session_id', unique=True)
    )

    talk_session_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    report: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('now()'))


class TalkSessions(Base):
    __tablename__ = 'talk_sessions'
    __table_args__ = (
        PrimaryKeyConstraint('talk_session_id', name='talk_sessions_pkey'),
    )

    talk_session_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    theme: Mapped[str] = mapped_column(String)
    scheduled_end_time: Mapped[datetime.datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    city: Mapped[Optional[str]] = mapped_column(String)
    prefecture: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(255))
    restrictions: Mapped[Optional[dict]] = mapped_column(JSONB)
    hide_report: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))


class TalksessionConsents(Base):
    __tablename__ = 'talksession_consents'
    __table_args__ = (
        PrimaryKeyConstraint('talksession_id', 'user_id', name='talksession_consents_pkey'),
    )

    talksession_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    consented_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    restrictions: Mapped[Optional[dict]] = mapped_column(JSONB)


class UserAuths(Base):
    __tablename__ = 'user_auths'
    __table_args__ = (
        PrimaryKeyConstraint('user_auth_id', name='user_auths_pkey'),
        Index('idx_user_id_user_subject', 'user_id', 'subject')
    )

    user_auth_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    provider: Mapped[str] = mapped_column(String)
    subject: Mapped[str] = mapped_column(String)
    is_verified: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('now()'))


class UserDemographics(Base):
    __tablename__ = 'user_demographics'
    __table_args__ = (
        PrimaryKeyConstraint('user_demographics_id', name='user_demographics_pkey'),
        Index('idx_user_demographics_user_id', 'user_id'),
        Index('user_demographics_user_id_index', 'user_id', unique=True)
    )

    user_demographics_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('now()'))
    date_of_birth: Mapped[Optional[str]] = mapped_column(String(255))
    occupation: Mapped[Optional[int]] = mapped_column(SmallInteger)
    gender: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String)
    household_size: Mapped[Optional[int]] = mapped_column(SmallInteger)
    prefecture: Mapped[Optional[str]] = mapped_column(String(255))


class UserGroupInfo(Base):
    __tablename__ = 'user_group_info'
    __table_args__ = (
        PrimaryKeyConstraint('talk_session_id', 'user_id', name='user_group_info_pkey'),
    )

    talk_session_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    group_id: Mapped[int] = mapped_column(Integer)
    pos_x: Mapped[float] = mapped_column(Double(53))
    pos_y: Mapped[float] = mapped_column(Double(53))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('now()'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('now()'))
    perimeter_index: Mapped[Optional[int]] = mapped_column(Integer)


class UserImages(Base):
    __tablename__ = 'user_images'
    __table_args__ = (
        PrimaryKeyConstraint('user_images_id', name='user_images_pkey'),
        Index('idx_user_images_user_id', 'user_id', 'archived')
    )

    user_images_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    key: Mapped[str] = mapped_column(String(255))
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    extension: Mapped[str] = mapped_column(String(20))
    archived: Mapped[bool] = mapped_column(Boolean, server_default=text('false'))
    url: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        PrimaryKeyConstraint('user_id', name='users_pkey'),
        Index('idx_users_user_id', 'user_id')
    )

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('now()'))
    email_verified: Mapped[bool] = mapped_column(Boolean, server_default=text('false'))
    display_id: Mapped[Optional[str]] = mapped_column(String)
    display_name: Mapped[Optional[str]] = mapped_column(String)
    icon_url: Mapped[Optional[str]] = mapped_column(String)
    email: Mapped[Optional[str]] = mapped_column(String(255))


class Votes(Base):
    __tablename__ = 'votes'
    __table_args__ = (
        PrimaryKeyConstraint('vote_id', name='votes_pkey'),
        Index('idx_votes_opinion_id_user_id', 'opinion_id', 'user_id'),
        Index('idx_votes_user_id_opinion_id', 'user_id', 'opinion_id'),
        Index('idx_votes_vote_id_opinion_id', 'vote_id', 'opinion_id')
    )

    vote_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    opinion_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    vote_type: Mapped[int] = mapped_column(SmallInteger)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('now()'))
    talk_session_id: Mapped[uuid.UUID] = mapped_column(Uuid)
