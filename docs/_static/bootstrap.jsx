import React, {useState} from 'react';
import ReactDOM from 'react-dom';

import Prism from 'prismjs';
import 'prismjs/components/prism-protobuf';
import 'prismjs/themes/prism.css';

const LANGUAGES = [
  {value: 'python', title: 'Python'},
  // {value: 'nodejs', title: 'NodeJS'},
  // {value: 'golang', title: 'Go'},
];

const WireType = {
    Input: 1,
    Output: 2,
};

const Accessibility = {
  Local: 'LOCAL',
  Namespace: 'NAMESPACE',
  Cluster: 'CLUSTER',
  External: 'EXTERNAL',
};

const Visibility = {
  Private: "PRIVATE",
  Headless: "HEADLESS",
  Internal: "INTERNAL",
  Public: "PUBLIC",
};

const Wires = [
  {
    runtime: "python",
    type: WireType.Input,
    value: "harness.wires.grpclib.client.ChannelWire",
    configType: "harness.grpc.Channel",
    dependencies: ['grpclib', 'protobuf'],
  },
  {
    runtime: "python",
    type: WireType.Output,
    value: "harness.wires.aiohttp.web.ServerWire",
    configType: "harness.http.Server",
    dependencies: ['aiohttp', 'cchardet'],
  },
];

const Imports = {
  'harness.grpc.Channel': 'harness/grpc.proto',
  'harness.http.Server': 'harness/http.proto',
};

function useSetter(setter) {
  return (event) => {
    setter(event.target.value)
  }
}

function itemSetter(value, setValue, i, name) {
  return (itemValue) => {
    setValue([
      ...value.slice(0, i),
      {...value[i], [name]: itemValue},
      ...value.slice(i + 1),
    ]);
  }
}

function itemDeleter(value, setValue, i) {
  return () => {
    setValue([
      ...value.slice(0, i),
      ...value.slice(i + 1),
    ]);
  }
}

function formatField(i, wire, options) {
  return `${wire.configType} ${wire.configName} = ${i} [\n        ${options.join(',\n        ')}\n    ];`;
}

function formatInput(i, wire, kubeEnabled) {
  let options = [`(harness.wire).input = "${wire.value}"`];
  if (kubeEnabled) {
    options.push(`(harness.wire).access = ${wire.accessibility}`);
  }
  return formatField(i, wire, options);
}

function formatOutput(i, wire, kubeEnabled) {
  let options = [`(harness.wire).output = "${wire.value}"`];
  if (kubeEnabled) {
    options.push(`(harness.wire).visibility = ${wire.visibility}`);
  }
  return formatField(i, wire, options);
}

function renderConfig(serviceName, kubeEnabled, repository, inputs, outputs) {
  const imports = ['harness/wire.proto'];
  inputs.map(w => {
    imports.push(Imports[w.configType]);
  });
  outputs.map(w => {
    imports.push(Imports[w.configType]);
  });

  let sourceLines = [
    `syntax = "proto3";`,
    '',
    `package ${serviceName};`,
  ];
  sourceLines.push('');
  imports.map(value => sourceLines.push(`import "${value}";`));
  sourceLines.push('');
  sourceLines.push(`message Configuration {`);
  sourceLines.push(`    option (harness.service).name = "${serviceName}";`);
  if (kubeEnabled) {
    sourceLines.push(`    option (harness.service).container.repository = "${repository}";`);
  }
  if (inputs.length > 0 || outputs.length > 0) {
    sourceLines.push('');
  }
  let fieldNumber = 1;
  inputs.map(w => {
    sourceLines.push(`    ${formatInput(fieldNumber, w, kubeEnabled)}`);
    fieldNumber++;
  });
  outputs.map(w => {
    sourceLines.push(`    ${formatOutput(fieldNumber, w, kubeEnabled)}`);
    fieldNumber++;
  });
  sourceLines.push('}');

  return Prism.highlight(
    sourceLines.join('\n'),
    Prism.languages.protobuf,
    'protobuf',
  );
}

function Input(props) {
  return (
    <div className="bootstrap-value bootstrap-wire">
      <span className="bootstrap-wire-value">{props.wire.value}</span>
      <div className="bootstrap-wire-inputs">
        <input className="bootstrap-wire-name" placeholder="name" type="text" value={props.wire.configName} onChange={useSetter(props.setConfigName)}/>
        {props.kubeEnabled &&
          <select value={props.wire.accessibility} onChange={useSetter(props.setAccessibility)}>
            {Object.entries(Accessibility).map(([key, value]) => {
              return <option key={value} value={value}>{key}</option>
            })}
          </select>
        }
        <button onClick={props.delete}>Delete</button>
      </div>
    </div>
  )
}

function Output(props) {
  return (
    <div className="bootstrap-value bootstrap-wire">
      <span className="bootstrap-wire-value">{props.wire.value}</span>
      <div className="bootstrap-wire-inputs">
        <input className="bootstrap-wire-name" placeholder="name" type="text" value={props.wire.configName} onChange={useSetter(props.setConfigName)}/>
        {props.kubeEnabled &&
          <select value={props.wire.visibility} onChange={useSetter(props.setVisibility)}>
            {Object.entries(Visibility).map(([key, value]) => {
              return <option key={value} value={value}>{key}</option>
            })}
          </select>
        }
        <button onClick={props.delete}>Delete</button>
      </div>
    </div>
  )
}

function AddWireDialog(props) {
  const [wire, setWire] = useState("");

  function addWire(event) {
    props.addWire(wire);
  }

  return <div className={props.className}>
    <select value={wire} onChange={useSetter(setWire)}>
      <option key={-1} value={""}>--- select ---</option>
      {Wires.map((wire, i) => {
        return <option key={i} value={wire.value}>{wire.value}</option>
      })}
    </select>
    <button onClick={addWire} disabled={wire === ""}>Add</button>
  </div>
}

function collectDependencies(inputs, outputs) {
  const items = new Set(['harness']);
  inputs.map(w => {
    w.dependencies.map(v => items.add(v));
  });
  outputs.map(w => {
    w.dependencies.map(v => items.add(v));
  });
  return Array.from(items).sort();
}

function Bootstrap() {
  const [serviceName, setServiceName] = useState('whisper');
  const [runtime, setRuntime] = useState('python');

  const [kubeEnabled, setKubeEnabled] = useState(true);
  const [repository, setRepository] = useState('registry.local/group/project');

  const [inputs, setInputs] = useState([]);
  const [outputs, setOutputs] = useState([]);

  function addWire(name) {
    let wire = Wires.find(wire => wire.value === name);
    if (wire.type === WireType.Input) {
      setInputs([...inputs, {
        ...wire,
        configName: '',
        accessibility: Accessibility.Cluster,
      }]);
    } else if (wire.type === WireType.Output) {
      setOutputs([...outputs, {
        ...wire,
        configName: '',
        visibility: Visibility.Internal,
      }]);
    } else {
      throw `Unknown wire type: ${wire.type}`
    }
  }

  let configMarkup = {__html: renderConfig(
    serviceName, kubeEnabled, repository, inputs, outputs,
  )};

  const dependencies = collectDependencies(inputs, outputs);

  return (
    <div className="bootstrap">
      <div className="bootstrap-row">
        <label className="bootstrap-key">Service Name</label>
        <input className="bootstrap-value" type="text" value={serviceName} onChange={useSetter(setServiceName)}/>
      </div>
      <div className="bootstrap-row">
        <label className="bootstrap-key">Runtime</label>
        <div className="bootstrap-value">
          {LANGUAGES.map(({value, title}) => {
            return (
              <label key={value}>
                <input type="radio" value={value}
                       checked={value === runtime}
                       onChange={useSetter(setRuntime)}/>
                {title}
              </label>
            )
          })}
        </div>
      </div>
      <div className="bootstrap-row">
        <label className="bootstrap-key">Kubernetes</label>
        <label className="bootstrap-value">
          <input type="checkbox" checked={kubeEnabled} onChange={() => {setKubeEnabled(!kubeEnabled)}}/>
          Enable
        </label>
      </div>
      {kubeEnabled && <div className="bootstrap-row">
        <label className="bootstrap-key">Docker Image Repository</label>
        <input className="bootstrap-value" type="text" value={repository} onChange={useSetter(setRepository)}/>
      </div>}
      <div className="bootstrap-row">
        <label className="bootstrap-key">Add Wire</label>
        <AddWireDialog className="bootstrap-value" addWire={addWire} />
      </div>
      <div>
        {inputs.map((w, i) => {
          return <div className="bootstrap-row" key={i}>
            <label className="bootstrap-key">Input</label>
            <Input wire={w}
                   kubeEnabled={kubeEnabled}
                   setConfigName={itemSetter(inputs, setInputs, i, 'configName')}
                   setAccessibility={itemSetter(inputs, setInputs, i, 'accessibility')}
                   delete={itemDeleter(inputs, setInputs, i)}/>
          </div>
        })}
      </div>
      <div>
        {outputs.map((w, i) => {
          return <div className="bootstrap-row" key={i}>
            <label className="bootstrap-key">Output</label>
            <Output wire={w}
                    kubeEnabled={kubeEnabled}
                    setConfigName={itemSetter(outputs, setOutputs, i, 'configName')}
                    setVisibility={itemSetter(outputs, setOutputs, i, 'visibility')}
                    delete={itemDeleter(outputs, setOutputs, i)}/>
          </div>
        })}
      </div>
      <div>
        <h3>Configuration</h3>
        <div>
          <pre dangerouslySetInnerHTML={configMarkup}/>
        </div>
      </div>
      <div>
        <h3>Dependencies</h3>
        <pre>{dependencies.join('\n')}</pre>
      </div>
    </div>
  )
}

const mountPoint = document.getElementById('placeholder');
ReactDOM.render(<Bootstrap/>, mountPoint);
