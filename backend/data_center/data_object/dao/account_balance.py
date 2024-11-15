from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from backend.service.utils import DatabaseUtils

Base = declarative_base()


def process_balance_response(api_response):
    if api_response.get('code') == '0':  # 确认请求成功
        balance_data = api_response.get('data', [])
        if balance_data and len(balance_data) > 0:
            return balance_data[0].get('details', [])
    return []


class AccountBalance(Base):
    __tablename__ = 'account_balance'

    id = Column(Integer, primary_key=True, autoincrement=True)
    avail_bal = Column(String, comment='可用余额')
    avail_eq = Column(String, comment='可用保证金')
    ccy = Column(String, comment='币种')
    eq = Column(String, comment='币种总权益')
    cash_bal = Column(String, comment='币种余额')
    u_time = Column(String, comment='币种余额信息的更新时间')
    dis_eq = Column(String, comment='美金层面币种折算权益')
    eq_usd = Column(String, comment='币种权益美金价值')
    notional_lever = Column(String, comment='币种杠杆倍数')
    ord_frozen = Column(String, comment='挂单占用')
    spot_iso_bal = Column(String, comment='现货逐仓余额')
    upl = Column(String, comment='未实现盈亏')
    spot_bal = Column(String, comment='现货余额')
    open_avg_px = Column(String, comment='现货开仓成本价')
    acc_avg_px = Column(String, comment='现货累计成本价')
    spot_upl = Column(String, comment='现货未实现收益')
    spot_upl_ratio = Column(String, comment='现货未实现收益率')
    total_pnl = Column(String, comment='现货累计收益')
    total_pnl_ratio = Column(String, comment='现货累计收益率')
    stop_loss_switch = Column(String, comment='自动止损开关')
    stop_loss_func_id = Column(Integer, comment='止损配置ID')
    limit_order_switch = Column(String, comment='自动限价开关')
    limit_order_func_id = Column(String, comment='限价委托配置ID')

    @staticmethod
    def process_balance_response(response_data):
        if response_data.get('code') == '0':  # 确认请求成功
            balance_data = response_data.get('data', [])
            if balance_data and len(balance_data) > 0:
                return balance_data[0].get('details', [])
        return []

    @staticmethod
    def insert_or_update(api_response):
        session = DatabaseUtils.get_db_session()
        details = AccountBalance.process_balance_response(api_response)

        for balance_detail in details:
            ccy = balance_detail.get('ccy', '')
            # 查找是否已存在该币种记录
            existing_balance = session.query(AccountBalance).filter(
                AccountBalance.ccy == ccy
            ).first()

            balance_data = {
                'avail_bal': balance_detail.get('availBal', ''),
                'avail_eq': balance_detail.get('availEq', ''),
                'eq': balance_detail.get('eq', ''),
                'cash_bal': balance_detail.get('cashBal', ''),
                'u_time': balance_detail.get('uTime', ''),
                'dis_eq': balance_detail.get('disEq', ''),
                'eq_usd': balance_detail.get('eqUsd', ''),
                'notional_lever': balance_detail.get('notionalLever', ''),
                'ord_frozen': balance_detail.get('ordFrozen', ''),
                'spot_iso_bal': balance_detail.get('spotIsoBal', ''),
                'upl': balance_detail.get('upl', ''),
                'spot_bal': balance_detail.get('spotBal', ''),
                'open_avg_px': balance_detail.get('openAvgPx', ''),
                'acc_avg_px': balance_detail.get('accAvgPx', ''),
                'spot_upl': balance_detail.get('spotUpl', ''),
                'spot_upl_ratio': balance_detail.get('spotUplRatio', ''),
                'total_pnl': balance_detail.get('totalPnl', ''),
                'total_pnl_ratio': balance_detail.get('totalPnlRatio', '')
            }

            if existing_balance:
                # 更新现有记录
                for key, value in balance_data.items():
                    setattr(existing_balance, key, value)
            else:
                # 创建新记录
                balance_data['ccy'] = ccy
                account_balance = AccountBalance(**balance_data)
                account_balance.stop_loss_switch = 'false'
                account_balance.limit_order_switch = 'false'
                session.add(account_balance)

        try:
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    def list_all():
        session = DatabaseUtils.get_db_session()
        try:
            # 添加过滤条件
            results = session.query(AccountBalance).filter(
                AccountBalance.eq_usd > '10'  # 由于存储为字符串，需要字符串比较
            ).all()
            return [
                {
                    'id': balance.id,
                    'ccy': balance.ccy,
                    'avail_bal': balance.avail_bal,
                    'avail_eq': balance.avail_eq,
                    'eq': balance.eq,
                    'cash_bal': balance.cash_bal,
                    'u_time': balance.u_time,
                    'dis_eq': balance.dis_eq,
                    'eq_usd': balance.eq_usd,
                    'notional_lever': balance.notional_lever,
                    'ord_frozen': balance.ord_frozen,
                    'spot_iso_bal': balance.spot_iso_bal,
                    'upl': balance.upl,
                    'spot_bal': balance.spot_bal,
                    'open_avg_px': balance.open_avg_px,
                    'acc_avg_px': balance.acc_avg_px,
                    'spot_upl': balance.spot_upl,
                    'spot_upl_ratio': balance.spot_upl_ratio,
                    'total_pnl': balance.total_pnl,
                    'total_pnl_ratio': balance.total_pnl_ratio,
                    'limit_order_switch': balance.limit_order_switch,
                    'limit_order_func_id': balance.limit_order_func_id,
                    'stop_loss_switch': balance.stop_loss_switch,
                    'stop_loss_func_id': balance.stop_loss_func_id

                }
                for balance in results
            ]
        finally:
            session.close()