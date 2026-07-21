import { Component } from "react";

// A render crash anywhere below this component (a bad prop, a bug in a
// child) would otherwise unmount the whole app to a blank white screen.
// Error boundaries are the one thing hooks still can't do — this has to
// be a class component, per React's own docs.
class ErrorBoundary extends Component {
  state = { error: null };

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error("Dashboard crashed:", error, info);
  }

  render() {
    if (this.state.error) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>{this.state.error.message}</p>
          <button type="button" className="button-primary" onClick={() => this.setState({ error: null })}>
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
