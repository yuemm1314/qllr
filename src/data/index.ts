/**
 * 数据源单例。整个应用都从这里取数据。
 * 切换数据源就改这一行。
 */
import { StaticDataSource } from './loadStaticData'
import type { DataSource } from './dataSource'

export const dataSource: DataSource = new StaticDataSource()
