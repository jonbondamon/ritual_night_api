from sqlalchemy import create_engine,Column, Integer, String, Boolean, ForeignKey, Date, UniqueConstraint, Text, DateTime
from sqlalchemy.orm import relationship, declarative_base, sessionmaker

Base = declarative_base()

class Stat(Base):
    __tablename__ = 'stats'
    stats_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, unique=True)
    minigames_completed = Column(Integer, default=0)
    games_won = Column(Integer, default=0)
    rituals_completed = Column(Integer, default=0)
    user = relationship("User", back_populates="stats")

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    gold_amount = Column(Integer, default=0)  # Added column for gold amount
    silver_amount = Column(Integer, default=0)  # Added column for silver amount
    stats = relationship("Stat", back_populates="user", uselist=False)
    user_items = relationship("UserItem", back_populates="user")
    xp_boosters = relationship("XPBooster", back_populates="user")
    referrals_made = relationship("Referral", foreign_keys="[Referral.referrer_user_id]", back_populates="referrer")
    referrals_received = relationship("Referral", foreign_keys="[Referral.referred_user_id]", back_populates="referred")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.stats:
            self.stats = Stat()

class Token(Base):
    __tablename__ = 'tokens'
    jti = Column(String, primary_key=True)

class Item(Base):
    __tablename__ = 'items'
    item_id = Column(Integer, primary_key=True)
    item_name = Column(String(255), nullable=False)
    item_type_id = Column(Integer, ForeignKey('item_types.item_type_id'), nullable=False)
    silver_cost = Column(Integer)
    gold_cost = Column(Integer)
    rarity_id = Column(Integer, ForeignKey('rarity_types.rarity_id'), nullable=False)
    unity_name = Column(String(255), nullable=False, unique=True)
    is_general_store_item = Column(Boolean, default=False, nullable=False)
    user_items = relationship("UserItem", back_populates="item")
    item_type = relationship("ItemType", back_populates="items")
    chromas = relationship("Chroma", back_populates="item")
    shaders = relationship("Shader", back_populates="item")
    items_level_progression = relationship("ItemsLevelProgression", back_populates="item")
    rarity = relationship("RarityType", back_populates="items")
    item_bundles = relationship("BundleItemAssociation", back_populates="item")
    premium_store_sets = relationship("SetItemAssociation", back_populates="item")

class ItemType(Base):
    __tablename__ = 'item_types'
    item_type_id = Column(Integer, primary_key=True)
    item_type_name = Column(String(255), nullable=False, unique=True)
    items = relationship("Item", back_populates="item_type")

class RarityType(Base):
    __tablename__ = 'rarity_types'
    rarity_id = Column(Integer, primary_key=True)
    rarity_name = Column(String(255), nullable=False, unique=True)
    items = relationship("Item", back_populates="rarity")

class UserItem(Base):
    __tablename__ = 'user_items'
    user_item_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.item_id'), nullable=False)
    item_level = Column(Integer, default=1)
    item_xp = Column(Integer, default=0)
    is_equipped = Column(Boolean, nullable=False)
    prestige_level = Column(Integer, default=0)
    selected_chroma_id = Column(Integer, ForeignKey('chromas.chroma_id'))
    selected_shader_id = Column(Integer, ForeignKey('shaders.shader_id'))
    favorite = Column(Boolean, default=False)
    __table_args__ = (UniqueConstraint('user_id', 'item_id'),)
    user = relationship("User", back_populates="user_items")
    item = relationship("Item", back_populates="user_items")
    selected_chroma = relationship("Chroma", back_populates="user_items")
    selected_shader = relationship("Shader", back_populates="user_items")

class ItemsLevelProgression(Base):
    __tablename__ = 'items_level_progression'
    progression_id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.item_id'), nullable=False)
    prestige_level = Column(Integer, nullable=False)
    level = Column(Integer, nullable=False)
    xp_required = Column(Integer, nullable=False)
    __table_args__ = (UniqueConstraint('item_id', 'prestige_level', 'level'),)
    item = relationship("Item", back_populates="items_level_progression")

class Chroma(Base):
    __tablename__ = 'chromas'
    chroma_id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.item_id'), nullable=False)
    chroma_name = Column(String(255), nullable=False)
    required_prestige_level = Column(Integer, nullable=False)
    required_item_level = Column(Integer, nullable=False)
    silver_price = Column(Integer, nullable=False)
    gold_price = Column(Integer, nullable=False)
    item = relationship("Item", back_populates="chromas")
    user_items = relationship("UserItem", back_populates="selected_chroma")

class Shader(Base):
    __tablename__ = 'shaders'
    shader_id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.item_id'), nullable=False)
    shader_name = Column(String(255), nullable=False)
    required_prestige_level = Column(Integer, nullable=False)
    required_item_level = Column(Integer, nullable=False)
    shader_type = Column(String(255), nullable=False)
    silver_price = Column(Integer, nullable=False)
    gold_price = Column(Integer, nullable=False)
    item = relationship("Item", back_populates="shaders")
    user_items = relationship("UserItem", back_populates="selected_shader")

class XPBooster(Base):
    __tablename__ = 'xp_boosters'
    booster_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    booster_type_id = Column(Integer, ForeignKey('booster_types.booster_type_id'), nullable=False)
    booster_effect = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=False)
    games_applied = Column(Integer, nullable=False)
    user = relationship("User", back_populates="xp_boosters")
    booster_type = relationship("BoosterType", back_populates="xp_boosters")

class BoosterType(Base):
    __tablename__ = 'booster_types'
    booster_type_id = Column(Integer, primary_key=True)
    booster_name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    xp_boosters = relationship("XPBooster", back_populates="booster_type")

class Referral(Base):
    __tablename__ = 'referrals'
    referral_id = Column(Integer, primary_key=True)
    referrer_user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    referred_user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    games_played = Column(Integer, default=0)
    reward_granted = Column(Boolean, default=False)
    date_referred = Column(Date, nullable=False)
    __table_args__ = (UniqueConstraint('referrer_user_id', 'referred_user_id'),)
    referrer = relationship("User", foreign_keys=[referrer_user_id], back_populates="referrals_made")
    referred = relationship("User", foreign_keys=[referred_user_id], back_populates="referrals_received")

class ItemBundle(Base):
    __tablename__ = 'item_bundles'
    bundle_id = Column(Integer, primary_key=True)
    bundle_name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    silver_price = Column(Integer, nullable=True)
    gold_price = Column(Integer, nullable=True) 
    bundle_items = relationship("BundleItemAssociation", back_populates="bundle")

class BundleItemAssociation(Base):
    __tablename__ = 'bundle_item_association'
    association_id = Column(Integer, primary_key=True)
    bundle_id = Column(Integer, ForeignKey('item_bundles.bundle_id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.item_id'), nullable=False)
    item = relationship("Item", back_populates="item_bundles")
    bundle = relationship("ItemBundle", back_populates="bundle_items")

class SetItemAssociation(Base):
    __tablename__ = 'set_item_association'
    association_id = Column(Integer, primary_key=True)
    set_id = Column(Integer, ForeignKey('premium_store_sets.set_id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.item_id'), nullable=False)
    premium_store_set = relationship("PremiumStoreSet", back_populates="items")
    item = relationship("Item", back_populates="premium_store_sets")


class PremiumStoreSet(Base):
    __tablename__ = 'premium_store_sets'
    set_id = Column(Integer, primary_key=True)
    set_name = Column(String(255), nullable=False, unique=True)
    items = relationship("SetItemAssociation", back_populates="premium_store_set")

class PremiumStoreSchedule(Base):
    __tablename__ = 'premium_store_schedules'
    schedule_id = Column(Integer, primary_key=True)
    set_id = Column(Integer, ForeignKey('premium_store_sets.set_id'), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    __table_args__ = (UniqueConstraint('set_id', 'start_date', 'end_date'),)
    
# Need to change database to support ssl 
engine = create_engine('postgresql://citus:Bingchillingjoncena1!@c-database.n6nx6pijv2sml4.postgres.cosmos.azure.com:5432/rndb?sslmode=require', echo=False)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)