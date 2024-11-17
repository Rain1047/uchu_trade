# scheduler_center/main.py
import logging.config
from typing import Dict, Any
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from backend.schedule_center.core.task_chain import TaskChain
from backend.schedule_center.tasks.common_task import DataFetchTask, AnalysisTask, ExecutionTask
from .core.base_task import TaskConfig

# 日志配置
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'scheduler.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['default', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
}


class SchedulerCenter:
    def __init__(self, config_path: str = 'config.yaml'):
        # 配置日志
        logging.config.dictConfig(LOGGING_CONFIG)
        self.logger = logging.getLogger(__name__)

        # 加载配置
        self.config = self._load_config(config_path)

        # 初始化调度器
        self.scheduler = BackgroundScheduler()
        self.task_chains: Dict[str, TaskChain] = {}

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {str(e)}")
            return {}

    def create_task_chain(self, chain_name: str) -> TaskChain:
        """创建任务链"""
        tasks = [
            DataFetchTask(f"{chain_name}_fetch"),
            AnalysisTask(f"{chain_name}_analysis"),
            ExecutionTask(f"{chain_name}_execution")
        ]

        chain = TaskChain(chain_name, tasks)
        self.task_chains[chain_name] = chain
        return chain

    def schedule_task_chain(self, chain_name: str, cron_config: Dict[str, str]):
        """调度任务链"""
        chain = self.task_chains.get(chain_name)
        if not chain:
            chain = self.create_task_chain(chain_name)

        self.scheduler.add_job(
            chain.execute,
            'cron',
            **cron_config,
            name=chain_name,
            id=chain_name
        )

    def start(self):
        """启动调度中心"""
        try:
            # 配置所有任务链
            for chain_config in self.config.get('task_chains', []):
                self.schedule_task_chain(
                    chain_config['name'],
                    chain_config['schedule']
                )

            self.scheduler.start()
            self.logger.info("Scheduler started successfully")

        except Exception as e:
            self.logger.error(f"Failed to start scheduler: {str(e)}")
            raise

    def stop(self):
        """停止调度中心"""
        self.scheduler.shutdown()
        self.logger.info("Scheduler stopped")


def main():
    # 创建调度中心实例
    scheduler_center = SchedulerCenter()

    try:
        # 启动调度中心
        scheduler_center.start()

        # 保持运行
        try:
            while True:
                pass
        except (KeyboardInterrupt, SystemExit):
            scheduler_center.stop()

    except Exception as e:
        logging.error(f"Scheduler center failed: {str(e)}", exc_info=True)
        scheduler_center.stop()
        raise


if __name__ == '__main__':
    main()
