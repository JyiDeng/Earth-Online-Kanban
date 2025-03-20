import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
from typing import Dict, List, Tuple
import seaborn as sns
from scipy import stats

class AnalyticsManager:
    def __init__(self, history_data: Dict):
        self.history_data = history_data
        self.reports_dir = "reports"
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False
        
    def generate_trend_chart(self, attribute: str, time_range: int = 30) -> str:
        """生成单个属性的趋势图
        
        Args:
            attribute: 属性名称
            time_range: 时间范围（天数）
            
        Returns:
            str: 保存的图表文件路径
        """
        timestamps = pd.to_datetime(self.history_data["timestamps"])
        values = self.history_data["attributes"][attribute]
        
        # 创建数据框
        df = pd.DataFrame({
            'timestamp': timestamps,
            'value': values
        })
        
        # 过滤最近time_range天的数据
        start_date = datetime.now() - timedelta(days=time_range)
        df = df[df['timestamp'] >= start_date]
        
        # 确保数据长度一致
        min_length = min(len(df['timestamp']), len(df['value']))
        df = df.iloc[:min_length]
        
        # 创建更小的图表
        plt.figure(figsize=(3, 3))
        
        # 设置更小的边距
        plt.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.2)
        
        # 绘制主曲线，减小标记大小
        plt.plot(df['timestamp'], df['value'], '-o', alpha=0.7, markersize=2)
        
        # 添加趋势线
        z = np.polyfit(range(len(df)), df['value'], 1)
        p = np.poly1d(z)
        plt.plot(df['timestamp'], p(range(len(df))), "r--", alpha=0.7, linewidth=1)
        
        # 设置标题和标签，使用更小的字体
        plt.title(f"{attribute}趋势图 - 最近{time_range}天", fontsize=8, pad=5)
        plt.xlabel("时间", fontsize=7)
        plt.ylabel("数值", fontsize=7)
        plt.grid(True, alpha=0.2)
        
        # 减小刻度标签的字体大小
        plt.xticks(rotation=45, fontsize=6, ha='right')
        plt.yticks(fontsize=6)
        
        # 调整布局，确保标签完全显示
        plt.tight_layout(pad=0.5)
        
        # 保存图表
        filename = f"{self.reports_dir}/{attribute}_trend_{datetime.now().strftime('%Y%m%d')}.png"
        plt.savefig(filename, bbox_inches='tight', dpi=300)
        plt.close()
        
        return filename
    
    def generate_weekly_report(self) -> str:
        """生成周报
        
        Returns:
            str: 报告文件路径
        """
        report_data = self._prepare_report_data(7)
        return self._generate_report(report_data, "周报")
    
    def generate_monthly_report(self) -> str:
        """生成月报
        
        Returns:
            str: 报告文件路径
        """
        report_data = self._prepare_report_data(30)
        return self._generate_report(report_data, "月报")
    
    def _prepare_report_data(self, days: int) -> Dict:
        """准备报告数据
        
        Args:
            days: 时间范围（天数）
            
        Returns:
            Dict: 报告数据
        """
        timestamps = pd.to_datetime(self.history_data["timestamps"])
        start_date = datetime.now() - timedelta(days=days)
        
        report_data = {
            "period_start": start_date.strftime("%Y-%m-%d"),
            "period_end": datetime.now().strftime("%Y-%m-%d"),
            "attributes": {}
        }
        
        for attr in self.history_data["attributes"]:
            values = pd.Series(self.history_data["attributes"][attr])
            df = pd.DataFrame({
                'timestamp': timestamps[:len(values)],  # 确保长度匹配
                'value': values
            })
            df = df[df['timestamp'] >= start_date]
            
            if len(df) > 0:
                report_data["attributes"][attr] = {
                    "average": df['value'].mean(),
                    "min": df['value'].min(),
                    "max": df['value'].max(),
                    "start": df['value'].iloc[0],
                    "end": df['value'].iloc[-1],
                    "trend": stats.linregress(range(len(df)), df['value']).slope
                }
        
        return report_data
    
    def _generate_report(self, data: Dict, report_type: str) -> str:
        """生成报告文件
        
        Args:
            data: 报告数据
            report_type: 报告类型（周报/月报）
            
        Returns:
            str: 报告文件路径
        """
        report = f"地球Online {report_type}\n"
        report += f"报告期间: {data['period_start']} 至 {data['period_end']}\n\n"
        
        # 分类统计
        categories = {
            "生理需求": ["饱腹", "口渴", "如厕", "瘦身指数", "心脏健康度"],
            "社会需求": ["社交", "情绪", "成就感", "情商", "安全感"],
            "能力属性": ["肌肉强度", "敏捷", "抗击打能力", "魅力", "道德"]
        }
        
        for category, attrs in categories.items():
            report += f"\n{category}:\n"
            report += "-" * 50 + "\n"
            
            for attr in attrs:
                if attr in data["attributes"]:
                    attr_data = data["attributes"][attr]
                    trend_symbol = "↑" if attr_data["trend"] > 0 else "↓" if attr_data["trend"] < 0 else "→"
                    
                    report += f"{attr}:\n"
                    report += f"  当前值: {attr_data['end']:.1f} {trend_symbol}\n"
                    report += f"  平均值: {attr_data['average']:.1f}\n"
                    report += f"  最大值: {attr_data['max']:.1f}\n"
                    report += f"  最小值: {attr_data['min']:.1f}\n"
                    report += f"  变化趋势: {attr_data['trend']:.4f}/天\n"
                    report += "\n"
        
        # 保存报告
        filename = f"{self.reports_dir}/earth_online_{report_type.lower()}_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
        
        return filename
    
    def generate_overview_chart(self) -> str:
        """生成属性总览图
        
        Returns:
            str: 保存的图表文件路径
        """
        # 准备数据
        current_values = {}
        for attr in self.history_data["attributes"]:
            if len(self.history_data["attributes"][attr]) > 0:
                current_values[attr] = self.history_data["attributes"][attr][-1]
        
        # 创建雷达图
        categories = {
            "生理需求": ["饱腹", "口渴", "如厕", "瘦身指数", "心脏健康度"],
            "社会需求": ["社交", "情绪", "成就感", "情商", "安全感"],
            "能力属性": ["肌肉强度", "敏捷", "抗击打能力", "魅力", "道德"]
        }
        
        # 创建一个更小的图表
        fig = plt.figure(figsize=(6, 2))
        
        for i, (category, attrs) in enumerate(categories.items(), 1):
            plt.subplot(1, 3, i)
            
            # 获取该类别的属性值
            values = [current_values.get(attr, 0) for attr in attrs]
            angles = np.linspace(0, 2*np.pi, len(attrs), endpoint=False)
            
            # 闭合多边形
            values = np.concatenate((values, [values[0]]))
            angles = np.concatenate((angles, [angles[0]]))
            
            # 绘制雷达图
            ax = plt.gca()
            ax.plot(angles, values)
            ax.fill(angles, values, alpha=0.25)
            
            # 设置刻度标签
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(attrs, fontsize=5)  # 减小字体大小
            plt.yticks(fontsize=6)  # 减小y轴字体大小
            
            # 设置标题
            plt.title(category, fontsize=8, pad=5)  # 减小标题字体大小和边距
            
        plt.tight_layout(pad=1.0)  # 减小子图之间的间距
        
        # 保存图表
        filename = f"{self.reports_dir}/overview_{datetime.now().strftime('%Y%m%d')}.png"
        plt.savefig(filename, bbox_inches='tight', dpi=300)
        plt.close()
        
        return filename 