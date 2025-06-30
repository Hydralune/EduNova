import { Router } from 'vue-router';

/**
 * 导航历史管理服务
 * 用于管理前进和后退的历史记录
 */
class NavigationService {
  private router: Router | null = null;
  private readonly HISTORY_KEY = 'navigationHistory';
  private readonly FORWARD_PATHS_KEY = 'navigationForwardPaths';
  private readonly MAX_HISTORY_LENGTH = 50;

  /**
   * 初始化导航服务
   * @param router Vue Router实例
   */
  public init(router: Router): void {
    this.router = router;

    // 监听路由变化
    router.afterEach((to, from) => {
      this.recordNavigation(from.fullPath, to.fullPath);
    });

    // 监听浏览器前进后退按钮
    window.addEventListener('popstate', () => {
      this.clearForwardPaths();
    });
  }

  /**
   * 记录导航历史
   * @param fromPath 来源路径
   * @param toPath 目标路径
   */
  private recordNavigation(fromPath: string, toPath: string): void {
    // 避免记录相同的路径
    if (fromPath === toPath) return;

    const history = this.getHistory();
    
    // 检查是否是通过浏览器的后退按钮导航
    if (history.length > 0 && history[history.length - 1] === toPath) {
      // 如果是后退，则不记录历史，但清除前进路径
      this.clearForwardPaths();
      return;
    }

    // 记录当前路径到历史
    history.push(fromPath);
    
    // 限制历史长度
    if (history.length > this.MAX_HISTORY_LENGTH) {
      history.shift();
    }
    
    this.saveHistory(history);
  }

  /**
   * 获取历史记录
   */
  private getHistory(): string[] {
    try {
      return JSON.parse(sessionStorage.getItem(this.HISTORY_KEY) || '[]');
    } catch {
      return [];
    }
  }

  /**
   * 保存历史记录
   */
  private saveHistory(history: string[]): void {
    sessionStorage.setItem(this.HISTORY_KEY, JSON.stringify(history));
  }

  /**
   * 获取前进路径列表
   */
  private getForwardPaths(): string[] {
    try {
      return JSON.parse(sessionStorage.getItem(this.FORWARD_PATHS_KEY) || '[]');
    } catch {
      return [];
    }
  }

  /**
   * 保存前进路径列表
   */
  private saveForwardPaths(paths: string[]): void {
    sessionStorage.setItem(this.FORWARD_PATHS_KEY, JSON.stringify(paths));
  }

  /**
   * 清除前进路径列表
   */
  private clearForwardPaths(): void {
    sessionStorage.removeItem(this.FORWARD_PATHS_KEY);
  }

  /**
   * 检查是否可以后退
   */
  public canGoBack(): boolean {
    return window.history.length > 1;
  }

  /**
   * 检查是否可以前进
   */
  public canGoForward(): boolean {
    return this.getForwardPaths().length > 0;
  }

  /**
   * 后退
   */
  public goBack(): void {
    if (!this.router || !this.canGoBack()) return;

    // 保存当前路径到前进路径列表
    const currentPath = this.router.currentRoute.value.fullPath;
    const forwardPaths = this.getForwardPaths();
    forwardPaths.push(currentPath);
    this.saveForwardPaths(forwardPaths);

    // 执行后退
    this.router.back();
  }

  /**
   * 前进
   */
  public goForward(): void {
    if (!this.router) return;

    const forwardPaths = this.getForwardPaths();
    if (forwardPaths.length > 0) {
      // 从前进路径列表中取出最后一个路径
      const nextPath = forwardPaths.pop() as string;
      this.saveForwardPaths(forwardPaths);
      
      // 导航到该路径
      this.router.push(nextPath);
    } else {
      // 如果没有前进路径，尝试使用浏览器的前进功能
      this.router.forward();
    }
  }
}

// 导出单例
export const navigationService = new NavigationService();
export default navigationService; 