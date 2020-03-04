import Prism from 'prismjs';
import 'prismjs/components/prism-protobuf';

Prism.languages.protobuf = Prism.languages.extend('protobuf', {
  'keyword': /\b(?:enum|import|message|oneof|option|package|repeated|service)(?:\s+)/,
});
Prism.languages.insertBefore('protobuf', 'operator', {
  'variable': /[A-Za-z_][\w.]*(?=\s*=)/,
});
