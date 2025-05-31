#!/usr/bin/env python3
"""
时区对比示例
展示UTC-4（美国东部时间）和UTC+8（中国时间）的K线数据差异
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.data_center.kline_data.okx_kline_fetcher import OkxKlineFetcher

def compare_timezones():
    """对比不同时区的K线数据"""
    
    print("=" * 80)
    print("时区对比示例：UTC-4 vs UTC+8")
    print("=" * 80)
    
    # 测试日期
    start_date = "2025-05-30"
    end_date = "2025-05-31"
    
    print(f"测试日期范围: {start_date} ~ {end_date}")
    print(f"测试交易对: BTC")
    print()
    
    # UTC-4 美国东部时间
    print("1️⃣ UTC-4 (美国东部时间)")
    print("-" * 40)
    fetcher_us = OkxKlineFetcher("/tmp/test_data", timezone_mode="UTC-4")
    df_us = fetcher_us.get_historical_data("BTC", "1d", start_date, end_date)
    
    if df_us is not None:
        print(f"数据条数: {len(df_us)} 条")
        print("数据详情:")
        for idx, row in df_us.iterrows():
            date_str = idx.strftime('%Y-%m-%d %H:%M:%S %Z')
            print(f"  📅 {date_str}")
            print(f"     开盘: ${row['open']:,.1f}")
            print(f"     收盘: ${row['close']:,.1f}")
            print(f"     成交量: {row['volume']:,.2f}")
            print()
        
        print("💡 说明:")
        print("   - 时间显示为美国东部时间00:00（午夜）")
        print("   - 5月31日数据 = 5月30日00:00-5月31日00:00(EDT)的交易")
        print("   - 适用于美国市场分析")
    else:
        print("❌ 无法获取UTC-4数据")
    
    print("\n" + "=" * 80)
    
    # UTC+8 中国时间
    print("2️⃣ UTC+8 (中国时间)")
    print("-" * 40)
    fetcher_cn = OkxKlineFetcher("/tmp/test_data", timezone_mode="UTC+8")
    df_cn = fetcher_cn.get_historical_data("BTC", "1d", start_date, end_date)
    
    if df_cn is not None:
        print(f"数据条数: {len(df_cn)} 条")
        print("数据详情:")
        for idx, row in df_cn.iterrows():
            date_str = idx.strftime('%Y-%m-%d %H:%M:%S %Z')
            print(f"  📅 {date_str}")
            print(f"     开盘: ${row['open']:,.1f}")
            print(f"     收盘: ${row['close']:,.1f}")
            print(f"     成交量: {row['volume']:,.2f}")
            print()
        
        print("💡 说明:")
        print("   - 时间显示为中国时间08:00")
        print("   - 5月31日数据 = 5月30日08:00-5月31日08:00(CST)的交易")
        print("   - 适用于亚洲市场分析")
    else:
        print("❌ 无法获取UTC+8数据")
    
    print("\n" + "=" * 80)
    
    # 对比分析
    print("3️⃣ 对比分析")
    print("-" * 40)
    
    if df_us is not None and df_cn is not None:
        print("🕐 时差关系:")
        print("   - UTC-4 vs UTC+8 = 相差12小时")
        print("   - 美国东部时间比中国时间早12小时")
        print("   - 美国5月31日00:00 = 中国5月31日12:00")
        print()
        
        print("📊 数据对比:")
        if len(df_us) > 0 and len(df_cn) > 0:
            # 比较最新一天的数据
            us_latest = df_us.iloc[-1]
            cn_latest = df_cn.iloc[-1]
            
            print(f"   最新收盘价:")
            print(f"   - 美国时间: ${us_latest['close']:,.1f}")
            print(f"   - 中国时间: ${cn_latest['close']:,.1f}")
            print(f"   - 价格差异: ${abs(us_latest['close'] - cn_latest['close']):,.1f}")
            print()
            
            print(f"   成交量对比:")
            print(f"   - 美国时间: {us_latest['volume']:,.2f}")
            print(f"   - 中国时间: {cn_latest['volume']:,.2f}")
            print()
        
        print("🎯 使用建议:")
        print("   - 分析美国市场 → 选择UTC-4")
        print("   - 分析亚洲市场 → 选择UTC+8")
        print("   - 全球统一标准 → 选择UTC")
    
    print("\n" + "=" * 80)
    print("示例完成！")
    print("=" * 80)


if __name__ == "__main__":
    compare_timezones() 