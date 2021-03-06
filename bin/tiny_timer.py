# -*- coding: utf-8 -*-

import time
import datetime
import traceback

from threading import Event, Thread, RLock


class _AbstractTimer(object):
    def run(self, time_stamp):
        """
        返回值 True 表示执行成功，返回 False
        """
        return True


class PeriodTimer(_AbstractTimer):
    def __init__(self, target, interval, max_run_count=None):
        self._run_count = 0
        self._target = target
        self._interval = interval
        self._max_run_count = max_run_count
        self._next_time = time.time() + interval

    def run(self, time_stamp):
        if time_stamp < self._next_time:
            return True

        self._next_time = time.time() + self._interval
        self._target()

        if self._max_run_count:
            return self._max_run_count > self._run_count
        return True


class FixedPeriodTimer(PeriodTimer):
    """
    设置固定时间的周期性定时器 D H
    """
    _TYPE_DICT = {
        'D': (24 * 3600, datetime.timedelta(days=1), '%Y%m%d'),
        'H': (3600, datetime.timedelta(hours=1), '%Y%m%d%H'),
        'M': (60, datetime.timedelta(minutes=1), '%Y%m%d%H%M')
    }

    def __init__(self, target, fix_type, max_run_count=None):
        if fix_type not in FixedPeriodTimer._TYPE_DICT:
            raise Exception('unknown FixedPeriodTimer type, should be "D"(per day) or "H"(per hour)')
        PeriodTimer.__init__(self, target, FixedPeriodTimer._TYPE_DICT[fix_type][0], max_run_count)

        self._next_time = FixedPeriodTimer._get_start_time(fix_type)

    @classmethod
    def _get_start_time(cls, fix_type):
        next_time = datetime.datetime.now() + FixedPeriodTimer._TYPE_DICT[fix_type][1]
        next_time = next_time.strftime(FixedPeriodTimer._TYPE_DICT[fix_type][2])
        next_time = datetime.datetime.strptime(next_time, FixedPeriodTimer._TYPE_DICT[fix_type][2])
        return time.mktime(next_time.timetuple())


class TinyTimerObserver:
    def __init__(self, logger):
        self._timer_dict = {}
        self._logger = logger

    def add(self, key, timer):
        if key in self._timer_dict:
            return False

        self._timer_dict[key] = timer
        self._logger.warn('TinyTimerObserver.add_timer: key = %s' % key)
        self._logger.warn('TinyTimerObserver: keys = %s' % self._timer_dict.keys())
        return True

    def remove(self, key):
        if key not in self._timer_dict:
            return False

        self._timer_dict.pop(key)
        self._logger.warn('TimerObserver.remove_timer: key = %s' % key)
        self._logger.warn('TinyTimerObserver: keys = %s' % self._timer_dict.keys())
        return True

    def clear(self):
        self._timer_dict.clear()
        self._logger.info('TimerObserver.clear_timer')

    def run(self):
        time_stamp = time.time()
        for key in self._timer_dict.keys():
            if not self._timer_dict[key].run(time_stamp):
                self._timer_dict.pop(key)
        self._logger.info('TinyTimerObserver: keys = %s' % self._timer_dict.keys())


class TinyThreadTimerObserver(Thread):
    def __init__(self, logger, min_interval=1):
        Thread.__init__(self)
        self._go = True
        self._logger = logger
        self._interval = min_interval

        self._lock = RLock()
        self._timer_dict = {}
        self._finish_event = Event()

    def add(self, key, timer):
        if key in self._timer_dict:
            return False

        with self._lock:
            self._timer_dict[key] = timer

        self._logger.warn('TinyThreadTimerObserver.add: key = %s' % key)
        self._logger.warn('TinyThreadTimerObserver: keys = %s' % self._timer_dict.keys())

        return True

    def remove(self, key):
        if key not in self._timer_dict:
            return False

        with self._lock:
            self._timer_dict.pop(key)

        self._logger.warn('TinyThreadTimerObserver.remove: key = %s' % key)
        self._logger.warn('TinyThreadTimerObserver: keys = %s' % self._timer_dict.keys())

        return True

    def clear(self):
        self._go = False
        self._finish_event.set()

        with self._lock:
            self._timer_dict.clear()
        self._logger.info('TinyThreadTimerObserver.clear_timer')

    def run(self):
        while self._go:
            self._finish_event.wait(timeout=self._interval)

            if self._finish_event.set():
                break

            time_stamp = time.time()
            for key in self._timer_dict.keys():
                try:
                    if not self._timer_dict[key].run(time_stamp):
                        self._timer_dict.pop(key)
                except Exception as ex:
                    self._logger.error(ex)
                    self._logger.warn(traceback.format_exc())

        self._logger.warn('TinyThreadTimerObserver.run: timer stopped, timer = %s' % self._timer_dict.keys())

